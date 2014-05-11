## @package log
# Logging wrappers.
#
# Wrap standard logging with formatting and file logging.

# system modules
import logging
import os
import sys
import traceback
import unittest

sys.dont_write_byte_code = True

LFORMAT = '%(asctime)s [%(levelname)s]:\t%(module)s:%(lineno)d: %(message)s'
DFORMAT = '%Y-%m-%d %H:%M:%S'

##
# @brief Logging mechanism
class CTFLogger(logging.Logger):
	##
	# @brief initialize a logging object
	#
	# @param args list of files to log to
	# @param kwargs use level= to set log level. default is DEBUG
	def __init__(self, *args, **kwargs):
		# call parent init
		logging.Logger.__init__(self, '', level=logging.DEBUG)
		stderr = True
		# optionally set the log level
		if 'level' in kwargs:
			self.setLevel(kwargs['level'])
		if 'stderr' in kwargs:
			stderr = kwargs['stderr']
		# set formatting
		fmt = logging.Formatter(LFORMAT, DFORMAT)
		# defaults to stderr
		if stderr:
			sh = logging.StreamHandler()
			sh.setFormatter(fmt)
			self.addHandler(sh)
		for f in args:
			fh = logging.FileHandler(f)
			fh.setFormatter(fmt)
			self.addHandler(fh)

	##
	# @brief log a critical error and exit
	#
	# @param msg the message
	# @param ec exit code
	def die(self, msg, ec=1):
		self.critical(msg + ' Exit %d' % ec)
		sys.exit(ec)

# Create a logging instance
l = CTFLogger()

##
# @brief handler for uncaught exception logging
#
# @param ex_cls exception name
# @param ex exception description
# @param tb traceback
def exceptions(ex_cls, ex, tb):
	trace = str.split(traceback.format_tb(tb)[0])
	exfile = trace[1].replace(',','').replace('"','')
	exline = trace[3].replace(',','')
	l.critical('%s:%s: %s: %s' % (exfile, exline, ex_cls, ex))

class TestLogger(unittest.TestCase):
	def test_init(self):
		self.assertTrue(CTFLogger())
		self.assertTrue(CTFLogger('test-data/test.log'))
		self.assertTrue(CTFLogger(level=logging.DEBUG))
		self.assertTrue(CTFLogger(level=logging.INFO))
		self.assertTrue(CTFLogger(level=logging.WARNING))
		self.assertTrue(CTFLogger(level=logging.ERROR))
		self.assertTrue(CTFLogger(level=logging.CRITICAL))
		self.assertTrue(CTFLogger(level='DEBUG'))
		self.assertTrue(CTFLogger(level='INFO'))
		self.assertTrue(CTFLogger(level='WARNING'))
		self.assertTrue(CTFLogger(level='ERROR'))
		self.assertTrue(CTFLogger(level='CRITICAL'))
		self.assertTrue(os.path.exists('test-data/test.log'))
		os.unlink('test-data/test.log')
	def test_log(self):
		t = CTFLogger('test-data/test.log', stderr=False)
		self.assertTrue(t)
		t.debug("debug")
		t.info("info")
		t.warning("warning")
		t.error("error")
		t.critical("critical")
		try:
			t.die("die")
		except SystemExit:
			pass
		try:
			t.die("die",ec=2)
		except SystemExit:
			pass

if __name__ == '__main__':
	# run from the same directory as the module
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	sys.exit(unittest.main(verbosity=2))
