#!/usr/bin/env python

import os
import sys
import web

sys.dont_write_byte_code = True
library_path = os.path.join(os.path.dirname(sys.argv[0]), './lib')
sys.path.append(library_path)

import log

render = web.template.render('templates/')

urls = (
	'/', 'index',
)

class index:
	def GET(self):
		name = web.cookies().get('testcookie')
		web.setcookie('testcookie', 'testvalue', 10, secure=True, httponly=True)
		return render.index(name)

if __name__ == "__main__":
	log.info("Starting web service.")
	app = web.application(urls, globals())
	app.run()
