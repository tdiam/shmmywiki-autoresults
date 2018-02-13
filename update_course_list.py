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
		courses[i] = course.replace("\n", "")

with open("db/keywords.json", "r", encoding="utf8") as f:
	keywords = json.load(f)

for i, course in courses.items():
	c = format_text(course)
	if c not in keywords.keys():
		keywords[c] = [int(i)]

shutil.copyfile("db/courses.json", "db/courses.json.bak")
shutil.copyfile("db/keywords.json", "db/keywords.json.bak")

fout = open("db/courses.json", "w", encoding="utf8")
fout.write(json.dumps(courses))
fout.close()

fout = open("db/keywords.json", "w", encoding="utf8")
fout.write(json.dumps(keywords))
fout.close()