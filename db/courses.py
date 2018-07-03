import csv
from db import keywords
from pprint import pprint
from utils import format_text

def get():
	courseList = {}
	with open("db/courses.csv", newline='') as f:
		reader = csv.reader(f)
		for course in reader:
			id, title, semester, flow, wiki = course
			courseList[id] = {"title": title, "semester": semester, "flow": flow, "wiki": wiki}
	return courseList

def print():
	pprint(get())

def update():
	courseList = get()
	kw = keywords.get()

	for id, course in courseList.items():
		c = format_text(course["title"])
		if c not in kw.keys():
			kw[c] = [int(id)]

	keywords.write(kw)