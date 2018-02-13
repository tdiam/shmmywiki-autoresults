import json
from pprint import pprint

with open("db/keywords.json") as f:
	data = json.load(f)

pprint(data)