#!/usr/bin/env python

# system modules
import logging
import os
import sys
import web

sys.dont_write_byte_code = True
rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.join(rootdir, 'lib'))

# local modules
import config
from log import l, exceptions

configfile = os.path.join('ctf-data/ctf.yaml')
render = web.template.render('templates/')
sys.excepthook = exceptions

urls = (
	'/', 'index',
)

##
# @brief index page
class index:
	##
	# @brief generate index
	#
	# @return index.html
	def GET(self):
		name = web.cookies().get('testcookie')
		web.setcookie('testcookie', 'testvalue', 10, secure=True, httponly=True)
		return render.index(name)

if __name__ == "__main__":
	# run from the same directory as the service file
	os.chdir(rootdir)
	c = config.Configurator()
	c.load(configfile)
	l.__init__(c.log, level=c.lvl)
	l.info("Starting web service.")
	app = web.application(urls, globals())
	app.run()
