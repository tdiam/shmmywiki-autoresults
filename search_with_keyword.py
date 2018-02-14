import json
from utils import format_text, find_in
from match_keywords import match_keywords

query = format_text(input("Search: "))
while query != "":
	res = match_keywords(query)
	if(len(res["indexes"]) == 0):
		print("Sorry, the course was not found in the list")
	else:
		print("\n".join(res["titles"]))
	query = format_text(input("Search: "))