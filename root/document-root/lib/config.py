## @package config
# Configuration management.
#
# Configurator class is responsible for servicing configuration information.

# system modules
import sys
import yaml

# local modules
import log

sys.dont_write_byte_code = True

##
# @brief Interface for configuration settings
class Configurator:
	##
	# @brief Load configuration file
	#
	# @param path file to load
	def load(self, path):
		log.debug("Loading config file %s." % path)
		with open(path, "r") as f:
			self._config = yaml.load(f)
	##
	# @return db file path
	@property
	def db(self):
		try:
			dbfile = self._config['db']['file']
			return dbfile
		except:
			log.error("No config entry 'db.file'")
			return None
	##
	# @return log file path
	@property
	def log(self):
		try:
			logfile = self._config['log']['file']
			return logfile
		except:
			log.error("No config entry 'log.file'")
			return None
	##
	# @return log level
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
