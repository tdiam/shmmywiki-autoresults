import json
from db import keywords
from utils import format_text, find_in

def run():
	query = format_text(input("Search: "))
	while query != "":
		res = keywords.match(query)
		if(len(res["indexes"]) == 0):
			print("Sorry, the course was not found in the list")
		else:
			output = ["[{}] {}".format(p[0], p[1]) for p in zip(res["indexes"], res["titles"])]
			print("\n".join(output))
		query = format_text(input("Search: "))
