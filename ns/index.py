import lxml.etree
import lxml.html
from lxml import etree
from lxml.etree import tostring

import os
from os import listdir
from os.path import isfile, join

if not os.path.exists("ns/indexed.txt"):
	open("ns/indexed.txt", "w+")
else:
	with open("ns/indexed.txt", "r") as f:
		indexed_docs = f.readlines()

indexed_docs = [x.strip() for x in indexed_docs] 

saved_documents = list(set([f for f in listdir("ns/documents") if isfile(join("ns/documents", f))]) - set(indexed_docs))

from elasticsearch import Elasticsearch
es = Elasticsearch()


def get_text(xpath,root,doc):
	if (len(root.xpath(xpath)) == 1):
		return root.xpath(xpath)[0].text_content()
	elif (len(root.xpath(xpath)) > 1):
		raise Exception('Multiple mathes for {} - {}'.format(xpath,doc))
	else:
		return None

def get_list(xpath,root,doc):
	if get_text(xpath,root,doc):
		return [x.strip() for x in get_text(xpath,root,doc).splitlines()]
	else:
		return None

for doc in saved_documents:
	with open('ns/documents/'+doc, 'r') as myfile:
		document_content=myfile.read()
	root = lxml.html.fromstring(document_content)
	for bad in root.xpath("//p[@class='fright']"):
		bad.getparent().remove(bad)
	soud = get_text("//table[@id='box-table-a']//tr[td='Soud:']/td[2]", root,doc)
	datum = get_text("//tr[td='Datum rozhodnutí:']/td[2]", root,doc)
	spzn =  get_list("//tr[td='Spisová značka:']/td[2]", root,doc)
	ecli = get_text("//tr[td='ECLI:']/td[2]", root,doc)
	typ = get_list("//tr[td='Typ rozhodnutí:']/td[2]", root,doc)
	katego = get_list("//tr[td='Kategorie rozhodnutí:']/td[2]", root,doc)
	heslo = get_list("//tr[td='Heslo:']/td[2]", root,doc)
	predpis = get_list("//tr[td='Dotčené předpisy:']/td[2]", root,doc)
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
	documentES = {
	'soud': soud,
	'datum': datum,
	'spzn': spzn,
	'ecli': ecli,
	'typ': typ,
	'katego':katego,
	'heslo': heslo,
	'predpis': predpis,
	'duvod': duvod, 
	'veta': veta,
	'sbirka': sbirka,
	'nazev': nazev,
	'senat': senat,
	'us_json': us_json,
	'content': content_text
	}
	res = es.index(index="my_index", doc_type='nsoud', id=doc, body=documentES)
	if res['result'] == "created" or res['result'] == "updated":
		with open("ns/indexed.txt", "a") as f:
			f.write(doc+"\n")
