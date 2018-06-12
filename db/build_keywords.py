import json
from db import keywords
from utils import format_text, find_in

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

def run():
	kw = keywords.get()

	c = format_text(input("Search: "))
	while(c != ""):
		res = keywords.match(c)
		if(len(res["indexes"]) == 0):
			print("Sorry, the course was not found in the list")
		elif(len(res["indexes"]) > 1):
			print("These courses satisfy your criteria, please narrow it down:")
			output = ["[{}] {}".format(p[0], p[1]) for p in zip(res["indexes"], res["titles"])]
			print("\n".join(output))
		else:
			i = res["indexes"][0]
			course = res["titles"][0]
			course_keywords = []
			for keyword, matches in kw.items():
				if i in matches:
					course_keywords.append(keyword)
			print("[{}] {}: {}".format(i, course, str(course_keywords)))
			print("(Re-enter a keyword to have it removed)")
			x = format_text(input())
			while(x != ""):
				if x not in kw:
					kw[x] = []
				if i in kw[x]:
					kw[x].remove(i)
				else:
					kw[x].append(i)
				x = format_text(input())
		c = format_text(input("Search: "))

	keywords.write(kw)