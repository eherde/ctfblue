## @package log
# Logging wrappers.
#
# Wrap standard logging with formatting and file logging.

# system modules
import inspect
import logging
import sys
import traceback

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
		# optionally set the log level
		if 'level' in kwargs:
			self.setLevel(kwargs['level'])
		# set formatting
		fmt = logging.Formatter(LFORMAT, DFORMAT)
		# defaults to stderr
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

def exceptions(ex_cls, ex, tb):
	l = CTFLogger('ctf-data/ctf.log')
	trace = str.split(traceback.format_tb(tb)[0])
	exfile = trace[1].replace(',','').replace('"','')
	exline = trace[3].replace(',','')
	l.critical('%s:%s: %s: %s' % (exfile, exline, ex_cls, ex))

if __name__ == '__main__':
	l = CTFLogger()
	l.debug("This is debug.")
	l.info("This is info.")
	l.warning("This is warning.")
	l.error("This is error.")
	l.critical("This is critical.")
