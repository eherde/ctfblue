import sys
import yaml

import log

sys.dont_write_byte_code = True

class Configurator:
	''' Class for configuration management. '''
	def __init__(self):
		self._config = None
	def load(self, path):
		log.debug("Loading config file %s." % path)
		with open(path, "r") as f:
			self._config = yaml.load(f)
	@property
	def db(self):
		try:
			dbfile = self._config['db']['file']
			return dbfile
		except:
			log.error("No config entry 'db.file'")
			return None
	@property
	def log(self):
		try:
			logfile = self._config['log']['file']
			return logfile
		except:
			log.error("No config entry 'log.file'")
			return None
	@property
	def lvl(self):
		try:
			loglvl = self._config['log']['level']
			return loglvl
		except:
			log.error("No config entry 'log.level'")
			return None

if __name__ == '__main__':
	pass
