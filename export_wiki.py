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
		# if the course exam results have been announced
		if key in results:
			rdate = results[key]["date"]
			rurl = "[" + results[key]["source"] + " forum]"
			if d:
				edate = d
				rdiffobj = datetime.strptime(rdate, "%d/%m/%Y") - datetime.strptime(d, "%d/%m/%Y")
				rdiff = "{:03d}".format(rdiffobj.days)
		fout.write("|[[{}]]||{}||{}||{}||{}\n|-\n".format(courses[key], edate, rdate, rdiff, rurl))
