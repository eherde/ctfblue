#!/usr/bin/env python

# system modules
import hashlib
import logging
import os
import sys
import web

sys.dont_write_byte_code = True
rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.join(rootdir, 'lib'))

# local modules
import config
import db
from log import l, exceptions

configfile = os.path.join('ctf-data/ctf.yaml')
render = web.template.render('templates/')
sys.excepthook = exceptions

global d
d = None

urls = (
	'/', 'index',
	'/adduser', 'adduser',
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

class adduser:
	def POST(self):
		l.info('POST adduser')
		i = web.input()
		if not i.has_key('username'):
			l.error('username field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing username')
		if not i.has_key('password'):
			l.error('password field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing password')
		# XXX: validate inputs
		username = str(i['username'])
		password = str(i['password'])
		h = hashlib.sha1()
		# hash password
		h.update(password)
		# hash with salt
		h.update(username)
		d = db.DB('ctf-data/ctf.db')
		l.debug('Creating new user %s' % username)
		guid = d.addUser(username, h.hexdigest())
		if not guid:
			return render.error(web.ctx.fullpath, 'EXISTS', 'username exists')
		return render.index(None)

if __name__ == "__main__":
	# run from the same directory as the service file
	os.chdir(rootdir)
	c = config.Configurator()
	c.load(configfile)
	l.__init__(c.log, level=c.lvl)
	d = db.DB(c.db)
	if not d:
		l.critical("Failed to initialize database.")
	l.info("Starting web service.")
	app = web.application(urls, globals())
	app.run()
