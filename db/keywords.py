import json
from db import courses
from pprint import pprint
from utils import format_text, find_in

def get():
	with open("db/keywords.json") as f:
		return json.load(f) 

def print():
	pprint(get())

def write(j):
	with open("db/keywords.json", "w", encoding="utf8") as fout:
		fout.write(json.dumps(j))

def match(text):
	kw = get()

	courseList = courses.get()
	res = {"indexes": [], "titles": []}
	if len(text) > 2 and \
	   text[0] == "[" and text[-1] == "]" and \
	   text[1:-1].isdigit() and \
	   text[1:-1] in courseList:
		res["indexes"].append(int(text[1:-1]))
		res["titles"].append(courseList[text[1:-1]]["title"])
		return res

	points = {i:0 for i in courseList}

	for keyword, matches in kw.items():
		if find_in(keyword, text):
			for match_id in matches:
				points[str(match_id)] += 1

	max_value = max(points.values())
	if(max_value == 0):
		return res
	for idx, p in points.items():
		if p == max_value:
			res["indexes"].append(int(idx))
			res["titles"].append(courseList[idx]["title"])
	return res

