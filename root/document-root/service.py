#!/usr/bin/env python

import sys
import web

sys.dont_write_byte_code = True

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
	app = web.application(urls, globals())
	app.run()
