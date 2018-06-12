#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from datetime import datetime

def format_text(text):
	text = text.lower()
	repl = [('ά', 'α'), ('έ', 'ε'), ('ή', 'η'), ('ί', 'ι'), ('ϊ', 'ι'), ('ΐ', 'ι'), ('ό', 'ο'), ('ύ', 'υ'), ('ϋ', 'υ'), ('ΰ', 'υ'), ('ώ', 'ω'), ('ς', 'σ')]
	for k, v in repl:
		text = text.replace(k, v)
	return text

def find_in(needle, haystack):
	return re.compile(r'\b({0})\b'.format(needle)).search(haystack)

def dmy_to_ymd(date):
	o = datetime.strptime(date, "%d/%m/%Y")
	return o.strftime("%Y/%m/%d")

def greekToEngDate(text):
	repl = [('Δευ', 'Mon'), ('Τρί', 'Tue'), ('Τετ', 'Wed'), ('Πέμ', 'Thu'), ('Παρ', 'Fri'), ('Σάβ', 'Sat'), ('Κυρ', 'Sun'), ('Ιαν', 'Jan'), ('Φεβ', 'Feb'), ('Μαρ', 'Mar'), ('Απρ', 'Apr'), ('Μάιος', 'May'), ('Ιουν', 'Jun'), ('Ιούλ', 'Jul'), ('Αύγ', 'Aug'), ('Σεπ', 'Sep'), ('Οκτ', 'Oct'), ('Νοέμ', 'Nov'), ('Δεκ', 'Dec')]
	for k, v in repl:
		text = text.replace(k, v, 1)
	return text