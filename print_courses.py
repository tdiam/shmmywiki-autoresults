import json
from pprint import pprint

with open("db/courses.json") as f:
	data = json.load(f)

pprint(data)