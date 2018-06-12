import json, pywikibot
from datetime import date, datetime, timedelta
from db import courses
from schedule import schedule
from results import results
from config import cfg

def get():
	with open("outputs/" + cfg.get("folder") + "/export_wiki.txt", "r", encoding="utf8") as f:
		return f.read()

def export():
	entries = []
	courseList = courses.get()
	dates = schedule.get()
	resultDates = results.get()

	for key, r in resultDates.items():
		if key not in dates:
			dates[key] = ""
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
		if d and d != "not assigned":
			edateobj = datetime.strptime(d, "%d/%m/%Y")
			# use %Y/%m/%d format to allow sorting of date columns
			edate = edateobj.strftime("%Y/%m/%d")
		# if the course exam results have been announced
		if key in resultDates:
			rdateobj = datetime.strptime(resultDates[key]["date"], "%d/%m/%Y")
			rdate = rdateobj.strftime("%Y/%m/%d")
			rurl = "[" + resultDates[key]["source"] + " forum]"
			if d and d != "not assigned":
				rdiffobj = rdateobj - edateobj
				rdiff = "{:03d}".format(rdiffobj.days)
		courseLink = courseList[key]["title"]
		if courseList[key]["wiki"]:
			courseLink = courseList[key]["wiki"] + "|" + courseLink
		semesterLink = "-"
		if courseList[key]["semester"]:
			semesterLink = "[[:Κατηγορία:{}ο Εξάμηνο|{}º]]".format(courseList[key]["semester"], courseList[key]["semester"])
		flowLink = "-"
		if courseList[key]["flow"]:
			flowLink = "[[:Κατηγορία:Ροή {}|{}]]".format(courseList[key]["flow"], courseList[key]["flow"])
		# use (max date - results date) as primary key so that the entries list will
		# be sorted in descending order of result dates
		# but ascending (alphabetical) order of course titles
		entries.append((datetime.max - rdateobj, courseLink, semesterLink, flowLink, edate, rdate, rdiff, rurl))

	entries.sort()

	with open("outputs/" + cfg.get("folder") + "/export_wiki.txt", "w", encoding="utf8") as fout:
		for entry in entries:
			fout.write("|[[{}]]||{}||{}||{}||{}||{}||{}\n|-\n".format(*entry[1:]))

# before running the bot, you should login `python pwb.py login` with the bot credentials in the shmmywiki site

def save():
	site = pywikibot.Site()
	# fetch the corresponding page of the course
	page = pywikibot.Page(site, cfg.get("wiki_title"))
	body = '{| class="sortable wikitable" style="text-align:left"' + "\n"
	body += '! Μάθημα !! Εξ. !! Ροή !! Εξέταση !! Αποτελέσματα !! Διαφορά !! class="unsortable"|Σύνδεσμος' + "\n"
	body += '|-' + "\n"
	body += get()
	body += "\n"
	body += '|}' + "\n"
	body += '----' + "\n"
	body += 'Disclaimer: Η παρούσα σελίδα παράγεται αυτόματα και είναι ακόμη σε δοκιμαστικό στάδιο, επομένως είναι πολύ πιθανό να περιέχει λανθασμένες πληροφορίες. Τα δεδομένα λαμβάνονται από το αντίστοιχο τόπικ αποτελεσμάτων.' + "\n"
	body += '[[Κατηγορία:Εξεταστική]]'
	page.text = body
	page.save(u"Update αποτελεσμάτων [Αυτόματη επεξεργασία από ShmmywikiBot (χειριστής Tdiam)]")
