#!/usr/bin/env python

# system modules
import logging
import os
import sys
import web

sys.dont_write_byte_code = True
rootdir = os.path.dirname(sys.argv[0])
datadir = 'ctf-data'

library_path = os.path.join(rootdir, './lib')
sys.path.append(library_path)

# local modules
import config
import log

configfile = os.path.join(rootdir, datadir, 'ctf.yaml')
render = web.template.render('templates/')

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
	c = config.Configurator()
	c.load(configfile)
	l = log.CTFLogger(c.log, level=c.lvl)
	l.info("Starting web service.")
	app = web.application(urls, globals())
	app.run()
