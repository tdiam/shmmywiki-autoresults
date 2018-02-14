import json
from utils import format_text, find_in
from pprint import pprint

def match_keywords(text):
	with open("db/keywords.json") as f:
		keywords = json.load(f)

	with open("db/courses.json") as f:
		courses = json.load(f)

	points = [0] * len(courses)

	for keyword, matches in keywords.items():
		if find_in(keyword, text):
			for match in matches:
				points[match] += 1

	max_value = max(points)
	res = {"indexes": [], "titles": []}
	if(max_value == 0):
		return res
	for idx, p in enumerate(points):
		if p == max_value:
			res["indexes"].append(idx)
			res["titles"].append(courses[str(idx)]["title"])
	return res