from match_keywords import match_keywords
from pyquery import PyQuery as pq
from urllib.request import urlopen
from datetime import datetime
from pprint import pprint
from utils import format_text, find_in, greekToEngDate
import sys, json, urllib

# URL from which results will be fetched
FORUM_URL = "https://shmmy.ntua.gr/forum/viewtopic.php?f=290&t=21986&start="

def readPage(url, start = 0):
	global postList, outputJSON
	f = urlopen(url + str(start)).read()
	html = pq(f)
	activeEl = html(".action-bar.top .pagination li.active span")
	if len(activeEl) == 0:
		curr = 0
	else:
		curr = int(activeEl.text())
	isLast = len(html(".action-bar.top .pagination li.next")) == 0
	posts = html("div.post")
	for p in posts:
		d = {}
		pobj = pq(p)

		# get content
		content = pobj("div.content")
		d["plain"] = content.text()
		d["html"] = content.html()

		# get corresponding course
		query = d["plain"]
		res = match_keywords(format_text(query))
		result = ""
		ind = ""
		while len(res["titles"]) != 1:
			result = "no result"
			break
			if len(res["titles"]) == 0:
				print("The following query could not be matched with a course:")
			else:
				print("The following query returned more than one result [" + ", ".join(res["titles"]) + "]")
			print(query)
			query = input("Try again: ")
			res = match_keywords(format_text(query))
		if result == "":
			result = res["titles"][0]
			ind = str(res["indexes"][0])
		d["course"] = result

		# get source url
		d["source"] = url + str(start) + "#" + p.attrib["id"]

		# get date
		date_str = pobj("p.author").html()
		i = date_str.index("» </span>") + 9
		date_str = greekToEngDate(date_str[i:-1])
		date_obj = datetime.strptime(date_str, "%a %b %d, %Y %I:%M %p")
		d["date"] = date_obj.strftime("%d/%m/%Y")
		postList += [d]
		if ind != "":
			outputJSON[ind] = {"source": d["source"], "date": d["date"]}
	if isLast == True:
		return
	else:
		readPage(url, curr * 20)

postList = []
outputJSON = {}
readPage(FORUM_URL)

with open("outputs/results.json", "w", encoding="utf8") as fout:
	fout.write(json.dumps(outputJSON))