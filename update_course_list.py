import shutil
import json
from utils import format_text

'''
Reads list.txt where the plain-text list of courses is contained
If there is a new course, it is added to the keywords.json file
with a single keyword matching it - its own name
'''

courses = {}

with open("db/course_list.txt") as f:
	data = f.readlines()
	for i, course in enumerate(data):
		course = course.replace("\n", "").split("|")
		courses[i] = {"title": course[0], "semester": course[1], "flow": course[2], "wiki": course[3]}

with open("db/keywords.json", "r", encoding="utf8") as f:
	keywords = json.load(f)

for i, course in courses.items():
	c = format_text(course["title"])
	if c not in keywords.keys():
		keywords[c] = [int(i)]

shutil.copyfile("db/courses.json", "db/courses.json.bak")
shutil.copyfile("db/keywords.json", "db/keywords.json.bak")

with open("db/courses.json", "w", encoding="utf8") as fout:
	fout.write(json.dumps(courses))

with open("db/keywords.json", "w", encoding="utf8") as fout:
	fout.write(json.dumps(keywords))