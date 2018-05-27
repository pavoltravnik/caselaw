#!/usr/bin/python
# requirements: "pip install lxml elasticsearch"
# usage: "python3 ns/links.py --month 1 --year 2018"

import lxml.etree
import lxml.html
from lxml import etree
from lxml.etree import tostring


from os import listdir
from os.path import isfile, join
saved_documents = [f for f in listdir("ns/documents") if isfile(join("ns/documents", f))]


def get_text(xpath,root,doc):
	if (len(root.xpath(xpath)) == 1):
		value = root.xpath(xpath)[0].text_content()
		return value
	elif (len(root.xpath(xpath)) > 1):
		raise Exception('Multiple mathes for {} - {}'.format(xpath,doc))
	else:
		return None


for doc in saved_documents:
	with open('ns/documents/'+doc, 'r') as myfile:
		document_content=myfile.read()
	root = lxml.html.fromstring(document_content)
	for bad in root.xpath("//p[@class='fright']"):
		bad.getparent().remove(bad)
	soud = get_text("//tr[td='Soud:']/td[2]", root,doc)
	datum = get_text("//tr[td='Datum rozhodnutí:']/td[2]", root,doc)
	spzn =  [x.strip() for x in get_text("//tr[td='Spisová značka:']/td[2]", root,doc).splitlines()]
	ecli = get_text("//tr[td='ECLI:']/td[2]", root,doc)
	typ = [x.strip() for x in get_text("//tr[td='Typ rozhodnutí:']/td[2]", root,doc).splitlines()]
	katego = [x.strip() for x in get_text("//tr[td='Kategorie rozhodnutí:']/td[2]", root,doc).splitlines()]
	heslo = [x.strip() for x in get_text("//tr[td='Heslo:']/td[2]", root,doc).splitlines()]
	predpis = [x.strip() for x in get_text("//tr[td='Dotčené předpisy:']/td[2]", root,doc).splitlines()]
	duvod = get_text("//tr[td='Důvod dovolání:']/td[2]", root,doc)
	veta = get_text("//tr[td='Právní věta:']/td[2]", root,doc)
	sbirka = get_text("//tr[td='Publikováno ve sbírce pod číslem:']/td[2]", root,doc)
	nazev = get_text("//tr[td='Název judikátu:']/td[2]", root,doc)
	senat = get_text("//tr[td='Senátní značka:']/td[2]", root,doc)
	stiznosti = root.xpath("//table[@id='box-table-a']//tr/td[1][contains(b[2]/font,'ústavní stížnost')]//table//tr[1]/td")
	us_json = {}
	if len(root.xpath("//table[@id='box-table-a']/tr/td[1][contains(b[2]/font,'ústavní stížnost')]")) == 1:
		for td in range(1, 1+len(stiznosti)):
			title = root.xpath("//table[@id='box-table-a']//tr/td[1][contains(b[2]/font,'ústavní stížnost')]//table//tr[1]/td["+str(td)+"]")[0].text_content().strip()
			us_value = root.xpath("//table[@id='box-table-a']//tr/td[1][contains(b[2]/font,'ústavní stížnost')]//table//tr[2]/td["+str(td)+"]")[0].text_content().strip()
			if title and us_value:
				us_json[title]= us_value
			## content_string = tostring(td, method='html', encoding="UTF-8").decode("utf-8")
			## print(content_string)
	elif len(stiznosti) > 1:
		raise Exception('Vic ustavnich stiznosti? - {}'.format(doc))
	# Parse content
	content = root.xpath("//div[@class='main_detail']/span/span")
	if len(content) == 1:
		content_text = content[0].text_content()
		content_html = tostring(content[0], method='html', encoding="UTF-8").decode("utf-8")
	else:
		raise Exception('No content was found - {}'.format(doc))
