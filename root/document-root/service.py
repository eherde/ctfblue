#!/usr/bin/env python

import logging
import os
import sys
import web

sys.dont_write_byte_code = True
rootdir = os.path.dirname(sys.argv[0])
datadir = 'ctf-data'

library_path = os.path.join(rootdir, './lib')
sys.path.append(library_path)

import config
import log

configfile = os.path.join(rootdir, datadir, 'ctf.yaml')
render = web.template.render('templates/')

urls = (
	'/', 'index',
)

class index:
	def GET(self):
		name = web.cookies().get('testcookie')
		web.setcookie('testcookie', 'testvalue', 10, secure=True, httponly=True)
		return render.index(name)

def configure_service():
	c = config.Configurator()
	c.load(configfile)
	if log.set_lvl(c.getLogLvl()):
		log.die("Failed to set default log level.")
	if log.add_logfile(c.getLogFile(), c.getLogLvl()):
		log.die("Failed to configure logging.")

if __name__ == "__main__":
	configure_service()
	log.info("Starting web service.")
	app = web.application(urls, globals())
	app.run()
