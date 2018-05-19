#!/usr/bin/python
# requirements: "pip install lxml multiprocessing requests"
# usage: "python3 links.py --sday 03 --smonth 01 --syear 2018 --eday 03 --emonth 01 --eyear 2018"

import re
import requests
import urllib.parse
import lxml.etree
import lxml.html
from lxml import etree
from lxml.etree import tostring
import os
import argparse
import multiprocessing

path="documents"
if not os.path.exists(path):
	os.makedirs(path)

parser = argparse.ArgumentParser()
parser.add_argument("--sday", help="start month", type=int)
parser.add_argument("--smonth", help="start month", type=int)
parser.add_argument("--syear", help="start year", type=int)
parser.add_argument("--eday", help="end month", type=int)
parser.add_argument("--emonth", help="end month", type=int)
parser.add_argument("--eyear", help="end year", type=int)
args = parser.parse_args()

address = "http://nsoud.cz/Judikatura/judikatura_ns.nsf/$$WebSearch1?SearchView&Query=%5Bdatum_predani_na_web%5D%3E%3D{0}%2F{1}%2F{2}%20AND%20%5Bdatum_predani_na_web%5D%3C%3D{3}%2F{4}%2F{5}&SearchOrder=2&SearchMax=0&Start=1&Count=1000&pohled=1".format(str(args.sday),str(args.smonth),str(args.syear),str(args.eday),str(args.emonth),str(args.eyear))

r = requests.get(address,allow_redirects=True)
root = lxml.html.fromstring(r.text)
links = root.xpath("//a/@href[starts-with(.,'/Judikatura/judikatura_ns.nsf/WebSearch')]")

print("Found {} links. \n".format(len(links)))

if len(links) > 990:
	raise Exception('Too many links in this period. Try to find another time period.')


# Write down links
for link in links:
	with open("links.txt", "a") as myfile:
		myfile.write(link+"\n")


def get_content(link):
	try:
		matchObj = re.match( r'\/Judikatura\/judikatura_ns\.nsf\/WebSearch\/(.*?)\?openDocument', link, re.M|re.I)
		if matchObj:
			q = requests.get("http://nsoud.cz"+link,allow_redirects=True)
			root = etree.HTML(q.text)
			a = root.xpath('//div[@id="content"]')[0]
			content = tostring(a, method='html', encoding="UTF-8").decode("utf-8")
			with open("documents/"+str(matchObj.group(1)+".html"), "a") as f:
				f.write(content)
		else:
			raise Exception('Parsing weblink error!')
	except Exception as e:
		raise Exception(str(e))


pool = multiprocessing.Pool(processes=8)
pool_outputs = pool.map(get_content,links)
pool.close()
pool.join()

print(" Saved {} documents. \n".format(len(pool_outputs)))
