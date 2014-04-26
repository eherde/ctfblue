import sys
import yaml

import log

sys.dont_write_byte_code = True

class Configurator:
	''' Class for configuration management. '''
	config = None
	def load(self, path):
		log.debug("Loading config file %s." % path)
		with open(path, "r") as f:
			self.config = yaml.load(f)
	def getDBFile(self):
		try:
			dbfile = self.config['db']['file']
			return dbfile
		except:
			log.error("No config entry 'db.file'")
			return None
	def getLogFile(self):
		try:
			logfile = self.config['log']['file']
			return logfile
		except:
			log.error("No config entry 'log.file'")
			return None
	def getLogLvl(self):
		try:
			loglvl = self.config['log']['level']
			return loglvl
		except:
			log.error("No config entry 'log.level'")
			return None

if __name__ == '__main__':
	pass
