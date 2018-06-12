from db import keywords
from pyquery import PyQuery as pq
from urllib.request import urlopen
from datetime import datetime
from pprint import pprint
from utils import format_text, find_in, greekToEngDate
import sys, json, urllib
from config import cfg

def getLast():
	try:
		with open("outputs/" + cfg.get("folder") + "/last_result_id.txt", "r") as fp:
			content = fp.read()
			if content:
				return content
			else:
				return "none"
	except FileNotFoundError:
		return "none"

def write(j):
	with open("outputs/" + cfg.get("folder") + "/results.json", "w", encoding="utf8") as fout:
		fout.write(json.dumps(j))

def get():
	with open("outputs/" + cfg.get("folder") + "/results.json", "r", encoding="utf8") as f:
		j = json.load(f)
	try:
		with open("outputs/" + cfg.get("folder") + "/results.manual.json", "r", encoding="utf8") as f:
			j_manual = json.load(f)
	except FileNotFoundError:
		j_manual = {}
	j.update(j_manual)
	return {i:j[i] for i in j if len(j[i]) > 0}

# stores the forum thread results to results.json and returns the number of new posts
def fetch():

	forum_url = cfg.get("forum_thread")
	if "&start=" not in forum_url:
		forum_url = forum_url + "&start="

	# store variables in mutable structure so that nested function will be able to change them
	data = {"lastID": getLast(), "lastIndex": -1, "postIndex": 0, "curr_lastID": ""}
	outputJSON = {}
	try:
		with open("outputs/" + cfg.get("folder") + "/results.ignore.json", "r", encoding="utf8") as f:
			ignore = json.load(f)
	except FileNotFoundError:
		ignore = []

	def readPage(url, start = 0):
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
			if p.attrib["id"] in ignore:
				continue
			d = {}
			pobj = pq(p)

			# get content
			content = pobj("div.content")
			d["plain"] = content.text()
			d["html"] = content.html()

			# get corresponding course
			query = d["plain"]
			res = keywords.match(format_text(query))
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
				res = keywords.match(format_text(query))
			if result == "":
				result = res["titles"][0]
				ind = str(res["indexes"][0])
			d["course"] = result

			# get source url
			d["source"] = url + str(start) + "#" + p.attrib["id"]
			if p.attrib["id"] == data["lastID"]:
				# store index when lastID post occurs
				data["lastIndex"] = data["postIndex"]
			data["curr_lastID"] = p.attrib["id"]

			# get date
			date_str = pobj("p.author").html()
			i = date_str.index("» </span>") + 9
			date_str = greekToEngDate(date_str[i:-1])
			date_obj = datetime.strptime(date_str, "%a %b %d, %Y %I:%M %p")
			d["date"] = date_obj.strftime("%d/%m/%Y")
			if ind != "" and ind not in outputJSON:
				data["postIndex"] += 1
				outputJSON[ind] = {"source": d["source"], "date": d["date"]}
		if isLast == True:
			return
		else:
			readPage(url, curr * 20)

	readPage(forum_url)

	newPosts = data["postIndex"] - 1 - data["lastIndex"]

	if newPosts > 0:
		with open("outputs/" + cfg.get("folder") + "/results.json", "w", encoding="utf8") as fout:
			fout.write(json.dumps(outputJSON))
		with open("outputs/" + cfg.get("folder") + "/last_result_id.txt", "w") as fp:
			fp.write(data["curr_lastID"])
	
	return newPosts
