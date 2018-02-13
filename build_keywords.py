import json
import shutil
from utils import format_text, find_in
from match_keywords import match_keywords

'''
	Tool to edit the keywords
	Outer loop:
		- search for course, stops when input is empty
		- prints course keywords
	Inner loop: keyword action
		- if input in keywords it will be removed
		- if not in keywords it will be added
		- stops when input is empty
'''

with open("db/keywords.json", "r", encoding="utf8") as f:
	keywords = json.load(f)

with open("db/courses.json", "r", encoding="utf8") as f:
	courses = json.load(f)

c = format_text(input("Search: "))
while(c != ""):
	res = match_keywords(c)
	if(len(res["indexes"]) == 0):
		print("Sorry, the course was not found in the list")
	elif(len(res["indexes"]) > 1):
		print("These courses satisfy your criteria, please narrow it down:")
		print("\n".join(res["titles"]))
	else:
		i = res["indexes"][0]
		course = res["titles"][0]
		course_keywords = []
		for keyword, matches in keywords.items():
			if i in matches:
				course_keywords.append(keyword)
		print(course + ": " + str(course_keywords))
		print("(Re-enter a keyword to have it removed)")
		x = format_text(input())
		while(x != ""):
			if x not in keywords:
				keywords[x] = []
			if i in keywords[x]:
				keywords[x].remove(i)
			else:
				keywords[x].append(i)
			x = format_text(input())
	c = format_text(input("Search: "))

shutil.copyfile("db/keywords.json", "db/keywords.json.bak")
shutil.copyfile("db/courses.json", "db/courses.json.bak")

fout = open("db/keywords.json", "w", encoding="utf8")
fout.write(json.dumps(keywords))
fout.close()