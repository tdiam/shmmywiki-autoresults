from match_keywords import match_keywords
from pyquery import PyQuery as pq
from urllib.request import urlopen
from datetime import datetime
from pprint import pprint
from utils import format_text, find_in, greekToEngDate
import sys, json, urllib

# URL from which results will be fetched
FORUM_URL = "https://shmmy.ntua.gr/forum/viewtopic.php?f=290&t=21986&start="

lastID = "none"

try:
	with open("outputs/last_result_id.txt", "r") as fp:
		content = fp.read()
		if content:
			lastID = content
except FileNotFoundError:
	pass

lastIndex = -1
curr_lastID = ""

def readPage(url, start = 0):
	global postList, outputJSON, lastIndex, curr_lastID
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
		if p.attrib["id"] == lastID:
			# current len(postList) will be equal to the index of this entry
			lastIndex = len(postList)
		curr_lastID = p.attrib["id"]

		# get date
		date_str = pobj("p.author").html()
		i = date_str.index("» </span>") + 9
		date_str = greekToEngDate(date_str[i:-1])
		date_obj = datetime.strptime(date_str, "%a %b %d, %Y %I:%M %p")
		d["date"] = date_obj.strftime("%d/%m/%Y")
		postList.append(d)
		if ind != "":
			outputJSON[ind] = {"source": d["source"], "date": d["date"]}
	if isLast == True:
		return
	else:
		readPage(url, curr * 20)

postList = []
outputJSON = {}
readPage(FORUM_URL)

newPosts = len(postList) - 1 - lastIndex
print("{} new posts fetched".format(newPosts))

if lastID != curr_lastID:
	with open("outputs/results.json", "w", encoding="utf8") as fout:
		fout.write(json.dumps(outputJSON))
	with open("outputs/last_result_id.txt", "w") as fp:
		fp.write(curr_lastID)
else:
	# if there are no new posts, abort the rest of the batch sequence
	exit()