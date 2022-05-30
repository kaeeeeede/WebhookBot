from collections import defaultdict
import yaml

class configurations:
	config = None

	@classmethod
	def init_config(cls):
		with open ('config.yaml', 'r+') as f:
			config = yaml.safe_load(f)
			config = defaultdict(cls.default_value, config)

		return config

	@classmethod
	def default_value(cls):
		return {}

	@classmethod
	def get_config(cls):
		if not cls.config:
			cls.config = cls.init_config()

		return cls.config

	@classmethod
	def reload_config(cls):
		with open ('config.yaml', 'r+') as f:
			latest_config = yaml.safe_load(f)
		
		cls.config.update(latest_config)
