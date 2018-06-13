class Config:
	configs = {}
	ctx = None
	def __init__(self, configFile = "config.json"):
		try:
			with open(configFile, "r", encoding="utf8") as f:
				import json
				self.configs = json.load(f)
		except FileNotFoundError:
			self.configs = {}

	def context(self, key):
		if key not in self.configs:
			raise ValueError("Config entry not found")
		else:
			self.ctx = self.configs[key]
	def get(self, prop):
		return self.ctx[prop]

cfg = Config()