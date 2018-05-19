#!/usr/bin/python
# requirements: "pip install lxml multiprocessing requests"
# usage: "python3 ns/links.py --month 1 --year 2018"

import re
import requests
import urllib.parse
import lxml.etree
import lxml.html
from lxml import etree
from lxml.etree import tostring
import os
import multiprocessing
import calendar
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("--month", help="start month", type=int)
parser.add_argument("--year", help="start year", type=int)
args = parser.parse_args()

path="ns/documents"
if not os.path.exists(path):
	os.makedirs(path)

from os import listdir
from os.path import isfile, join
saved_documents = [os.path.splitext(f)[0] for f in listdir("ns/documents") if isfile(join("ns/documents", f))]


def parse_month(parse_year,parse_month):
	for day in range(1, calendar.monthrange(parse_year,parse_month)[1]):
		parse_decisions(parse_year,parse_month,day)


def parse_decisions(year,month,day):
	address = "http://nsoud.cz/Judikatura/judikatura_ns.nsf/$$WebSearch1?SearchView&Query=%5Bdatum_predani_na_web%5D%3E%3D{0}%2F{1}%2F{2}%20AND%20%5Bdatum_predani_na_web%5D%3C%3D{3}%2F{4}%2F{5}&SearchOrder=2&SearchMax=0&Start=1&Count=1000&pohled=1".format(str(day),str(month),str(year),str(day),str(month),str(year))
	count = 0
	while (count < 10):
		count = count + 1
		try:
			r = requests.get(address,allow_redirects=True)
		except Exception as e:
			print("{} - {}".format(matchObj, e))
		if q.status == 200:
			break
		else:
			time.sleep(5)
	root = lxml.html.fromstring(r.text)
	links = root.xpath("//a/@href[starts-with(.,'/Judikatura/judikatura_ns.nsf/WebSearch')]")
	if len(links) > 990:
		raise Exception('Too many links in this period ({}). {}-{}-{}'.format(len(links),day,month,year))

	# Write down links
	for link in links:
		with open("ns/links.txt", "a") as myfile:
			myfile.write(link+"\n")

	pool = multiprocessing.Pool(processes=4)
	pool_outputs = pool.map(get_content,links)
	pool.close()
	pool.join()
	print("{}\t{}\t{}-{}-{}".format(len(links),len(pool_outputs),day,month,year))

def get_content(link):
	try:
		matchObj = re.match( r'\/Judikatura\/judikatura_ns\.nsf\/WebSearch\/(.*?)\?openDocument', link, re.M|re.I)
		if matchObj and matchObj not in saved_documents:
			count = 0
			while (count < 10):
				count = count + 1
				try:
					q = requests.get("http://nsoud.cz"+link,allow_redirects=True)
				except Exception as e:
					print("{} - {}".format(matchObj, e))
				if q.status == 200:
					break
				else:
					time.sleep(5)
			root = etree.HTML(q.text)
			a = root.xpath('//div[@id="content"]')[0]
			content = tostring(a, method='html', encoding="UTF-8").decode("utf-8")
			with open("ns/documents/"+str(matchObj.group(1)+".html"), "a") as f:
				f.write(content)
		else:
			raise Exception('Parsing weblink error!')
	except Exception as e:
		raise Exception(str(e))

if __name__ == '__main__':
    # service.py executed as script
    # do something
    parse_month(args.year, args.month)