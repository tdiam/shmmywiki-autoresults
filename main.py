from wiki import wiki
from results import results
from schedule import schedule
from db import courses, search_with_keyword, build_keywords
from config import cfg
from utils import dmy_to_ymd
import sys, os

try:
	cfg.context(sys.argv[1])
	if not os.path.isdir("outputs/" + cfg.get("folder")):
		os.makedirs("outputs/" + cfg.get("folder"))
except ValueError as err:
	print("Error: {}".format(err))
	sys.exit(1)
except IndexError:
	print("Usage: python main.py _context_")
	sys.exit(1)

try:
	actions = sys.argv[2].split(",")
except IndexError:
	results.fetch()
	wiki.export()
	wiki.save()
	exit(0)

if "search" in actions:
	search_with_keyword.run()
	exit(0)
if "build_keywords" in actions:
	build_keywords.run()
	exit(0)
if "courses_update" in actions:
	courses.update()
if "schedule" in actions:
	schedule.parse()
if "print_schedule" in actions:
	d_obj = schedule.get()
	courses = courses.get()
	null_dates = [("?", courses[c]["title"], c) for c, d in d_obj.items() if d is None or d in ["ERROR", "not assigned"]]
	dates = [(dmy_to_ymd(d), courses[c]["title"], c) for c, d in d_obj.items() if d is not None and d not in ["ERROR", "not assigned"]]
	for d, course, idx in null_dates:
		print("{}: [{}] {}".format(d, idx, course))
	for d, course, idx in sorted(dates):
		print("{}: [{}] {}".format(d, idx, course))
if "results" in actions:
	results.fetch()
if "print_results" in actions:
	results = results.get()
	courses = courses.get()
	dates = [(dmy_to_ymd(r["date"]), courses[c]["title"], c) for c, r in results.items()]
	for d, course_title, idx in sorted(dates):
		print("{}: [{}] {}".format(d, idx, course_title))
if "wiki" in actions:
	wiki.export()
	wiki.save()
if "export_wiki" in actions:
	wiki.export()
