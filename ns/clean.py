import lxml.etree
import lxml.html
from lxml import etree
from lxml.etree import tostring

import os
from os import listdir
from os.path import isfile, join
saved_documents = [f for f in listdir("ns/documents") if isfile(join("ns/documents", f))]


for doc in saved_documents:
	try:
		with open('ns/documents/'+doc, 'r') as myfile:
			document_content=myfile.read()
	except:
		print("ERROR "+doc+"\n")
		os.remove('ns/documents/'+doc)
	try:
		root = lxml.html.fromstring(document_content)
	except:
		print("ERROR "+doc+"\n")
		os.remove('ns/documents/'+doc)
	try:
		if (len(root.xpath("//div[@class='main_detail']")) > 1):
			print('Multiple mathes for {} - {}'.format("//div[@class='main_detail']",doc))
			os.remove('ns/documents/'+doc)
	except:
		print("ERROR "+doc+"\n")
		os.remove('ns/documents/'+doc)