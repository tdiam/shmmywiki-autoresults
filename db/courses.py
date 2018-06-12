import json
from db import keywords
from pprint import pprint
from utils import format_text

def get():
	with open("db/courses.json") as f:
		return json.load(f)

def print():
	pprint(get())

def write(j):
	with open("db/courses.json", "w", encoding="utf8") as fout:
		fout.write(json.dumps(j))

def update():
	courseList = {}

	with open("db/course_list.txt") as f:
		data = f.readlines()
		for i, course in enumerate(data):
			course = course.replace("\n", "").split("|")
			courseList[i] = {"title": course[0], "semester": course[1], "flow": course[2], "wiki": course[3]}

	kw = keywords.get()

	for i, course in courseList.items():
		c = format_text(course["title"])
		if c not in kw.keys():
			kw[c] = [int(i)]

	write(courseList)
	keywords.write(kw)