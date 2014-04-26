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
			return self._config['db']['file']
		except:
			return None
	##
	# @return log file path
	@property
	def log(self):
		try:
			return self._config['log']['file']
		except:
			return None
	##
	# @return log level
	@property
	def lvl(self):
		try:
			return self._config['log']['level']
		except:
			return None

if __name__ == '__main__':
	c = Configurator()
	c.load('../ctf-data/ctf.yaml')
