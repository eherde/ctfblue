import inspect
import logging
import sys

sys.dont_write_byte_code = True

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG)

def err_fmt():
	# get the frame we want
	p = inspect.getouterframes(inspect.currentframe())[-1]
	# return the formated file and linenumber
	return '%s:%d:' % (p[1],p[2])

def debug(msg):
	logging.debug(err_fmt() + ' ' + msg)

def info(msg):
	logging.info(msg)

def warning(msg):
	logging.warning(msg)

def error(msg):
	logging.error(msg)

def critical(msg):
	logging.critical(err_fmt() + ' ' + msg)

if __name__ == '__main__':
	debug("This is debug.")
	info("This is info.")
	warning("This is warning.")
	error("This is error.")
	critical("This is critical.")
