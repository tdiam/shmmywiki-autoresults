class Config:
	configs = { \
		"spring18": { \
			"folder": "spring18", \
			"schedule_file": "schedule_jun18.pdf", \
			"wiki_title": "Εξεταστική_Εαρινή_2018", \
			"forum_thread": "https://shmmy.ntua.gr/forum/viewtopic.php?f=290&t=22175" \
		}, \
		"winter18": { \
			"folder": "winter18", \
			"schedule_file": "schedule_jan18.pdf", \
			"wiki_title": "Εξεταστική_Χειμερινή_2018", \
			"forum_thread": "https://shmmy.ntua.gr/forum/viewtopic.php?f=290&t=21986" \
		}, \
		"sept17": { \
			"folder": "sept17", \
			"schedule_file": "schedule_sept17.pdf", \
			"wiki_title": "Εξεταστική_Επαναληπτική_2017", \
			"forum_thread": "https://shmmy.ntua.gr/forum/viewtopic.php?f=290&t=21695" \
		} \
	}
	ctx = None

	def context(self, key):
		if key not in self.configs:
			raise ValueError("Config entry not found")
		else:
			self.ctx = self.configs[key]
	def get(self, prop):
		return self.ctx[prop]

cfg = Config()