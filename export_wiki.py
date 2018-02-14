import json
from datetime import date, datetime, timedelta

'''
	Generate wiki table with results
	The scripts pdfparse.py and fetch.py have to be run first
'''

with open("db/courses.json", "r", encoding="utf8") as f:
	courses = json.load(f)
with open("outputs/dates.json", "r", encoding="utf8") as f:
	dates = json.load(f)
with open("outputs/results.json", "r", encoding="utf8") as f:
	results = json.load(f)

with open("outputs/export_wiki.txt", "w", encoding="utf8") as fout:
	entries = []

	for key, d in dates.items():
		'''
			edate: Exam date
			rdate: Results date
			rdiff: Difference between results and exam date (in days)
			rurl: Results link
		'''
		edate = "-"
		rdate = "-"
		rdiff = "-"
		rurl = "-"
		rdateobj = datetime.min
		edateobj = datetime.min
		if d:
			edateobj = datetime.strptime(d, "%d/%m/%Y")
			# use %Y/%m/%d format to allow sorting of date columns
			edate = edateobj.strftime("%Y/%m/%d")
		# if the course exam results have been announced
		if key in results:
			rdateobj = datetime.strptime(results[key]["date"], "%d/%m/%Y")
			rdate = rdateobj.strftime("%Y/%m/%d")
			rurl = "[" + results[key]["source"] + " forum]"
			if d:
				rdiffobj = rdateobj - edateobj
				rdiff = "{:03d}".format(rdiffobj.days)
		# use (max date - results date) as primary key so that the entries list will
		# be sorted in descending order of result dates
		# but ascending (alphabetical) order of course titles
		courseLink = courses[key]["title"]
		if courses[key]["wiki"]:
			courseLink = courses[key]["wiki"] + "|" + courseLink
		semesterLink = "-"
		if courses[key]["semester"]:
			semesterLink = "[[:Κατηγορία:{}ο Εξάμηνο|{}º]]".format(courses[key]["semester"], courses[key]["semester"])
		flowLink = "-"
		if courses[key]["flow"]:
			flowLink = "[[:Κατηγορία:Ροή {}|{}]]".format(courses[key]["flow"], courses[key]["flow"])
		entries.append((datetime.max - rdateobj, courseLink, semesterLink, flowLink, edate, rdate, rdiff, rurl))

	entries.sort()

	for entry in entries:
		fout.write("|[[{}]]||{}||{}||{}||{}||{}||{}\n|-\n".format(*entry[1:]))
