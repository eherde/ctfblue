import inspect
import logging
import sys

sys.dont_write_byte_code = True

LFORMAT = '%(asctime)s [%(levelname)s]: %(message)s'
DFORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=LFORMAT, datefmt=DFORMAT)

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

def die(msg, ec=1):
	critical(msg + ' Exit %d.' % ec)
	sys.exit(ec)

def set_lvl(lvl):
	if not lvl:
		return -1
	logging.getLogger().setLevel(lvl)

def add_logfile(path, lvl=logging.INFO):
	if not path or not lvl:
		return -1
	root_logger = logging.getLogger()
	fmt = logging.Formatter(LFORMAT, DFORMAT)
	fh = logging.FileHandler(path)
	fh.setLevel(lvl)
	fh.setFormatter(fmt)
	root_logger.addHandler(fh)
	return 0

if __name__ == '__main__':
	add_logfile('test.log')
	debug("This is debug.")
	info("This is info.")
	warning("This is warning.")
	error("This is error.")
	critical("This is critical.")
