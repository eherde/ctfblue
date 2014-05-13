## @package config
# Configuration management.
#
# Configurator class is responsible for servicing configuration information.

# system modules
import os
import sys
import unittest
import yaml

sys.dont_write_byte_code = True

##
# @brief Interface for configuration settings
class Configurator:
	def __init__(self):
		self._secret = None
	##
	# @brief Load configuration file
	#
	# @param path file to load
	def load(self, path):
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
	##
	# @return log level
	@property
	def secret(self):
		if self._secret is None:
			try:
				keyfile = self._config['secret']['file']
			except (IOError, KeyError):
				return None
			with file(keyfile) as f:
				self._secret = f.read()
		return self._secret

class TestConfigurator(unittest.TestCase):
	def test_init(self):
		self.assertTrue(Configurator())
	def test_load(self):
		c = Configurator()
		self.assertTrue(c)
		self.assertTrue(c.load('test-data/ctf.yaml') is None)
		self.assertRaises(IOError, c.load, '')

if __name__ == '__main__':
	# run from the same directory as the module
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	sys.exit(unittest.main(verbosity=2))
