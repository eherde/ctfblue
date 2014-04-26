## @package log
# Logging wrappers.
#
# Wrap standard logging with formatting and file logging.

# system modules
import inspect
import logging
import sys

sys.dont_write_byte_code = True

LFORMAT = '%(asctime)s [%(levelname)s]: %(message)s'
DFORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=LFORMAT, datefmt=DFORMAT)

##
# @brief generate the file and line number information
# of the function calling the logging mechanism
#
# @return string of error message
def err_fmt():
	# get the frame we want
	p = inspect.getouterframes(inspect.currentframe())[-1]
	# return the formated file and linenumber
	return '%s:%d:' % (p[1],p[2])

##
# @brief log a debug message
#
# @param msg the message
def debug(msg):
	logging.debug(err_fmt() + ' ' + msg)

##
# @brief log an info message
#
# @param msg the message
def info(msg):
	logging.info(msg)

##
# @brief log a warning message
#
# @param msg the message
def warning(msg):
	logging.warning(msg)

##
# @brief log an error message
#
# @param msg the message
def error(msg):
	logging.error(msg)

##
# @brief log a critical message
#
# @param msg the message
def critical(msg):
	logging.critical(err_fmt() + ' ' + msg)

##
# @brief log a critical message and exit
#
# @param msg the message
# @param ec exit code
def die(msg, ec=1):
	critical(msg + ' Exit %d.' % ec)
	sys.exit(ec)

##
# @brief set the global log level
#
# @param lvl the level
def set_lvl(lvl):
	if not lvl:
		return -1
	logging.getLogger().setLevel(lvl)

##
# @brief add a logfile
#
# @param path the logfile
# @param lvl the loglevel for this file
def add_logfile(path, lvl=logging.INFO):
	if not path or not lvl:
		return -1
	root_logger = logging.getLogger()
	fmt = logging.Formatter(LFORMAT, DFORMAT)
	fh = logging.FileHandler(path)
	fh.setLevel(lvl)
	fh.setFormatter(fmt)
	root_logger.addHandler(fh)

if __name__ == '__main__':
	add_logfile('test.log')
	debug("This is debug.")
	info("This is info.")
	warning("This is warning.")
	error("This is error.")
	critical("This is critical.")
