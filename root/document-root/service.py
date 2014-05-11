#!/usr/bin/env python

# system modules
import hashlib
import os
import sys
import time
import web

sys.dont_write_byte_code = True
rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.join(rootdir, 'lib'))

# local modules
import config
import db
import scp
from log import l, exceptions

configfile = os.path.join('ctf-data/ctf.yaml')
render = web.template.render('templates/')
sys.excepthook = exceptions

urls = (
	'/', 'index',
	'/adduser', 'adduser',
	'/logon', 'logon'
)

def logon_redirect():
	return web.seeother('/logon')

##
# @brief index page
class index:
	##
	# @brief generate index
	#
	# @return index.html
	def GET(self):
		l.info('GET index')
		name = web.cookies().get('testcookie')
		web.setcookie('testcookie', 'testvalue', 10, secure=True, httponly=True)
		return render.index(name)

class adduser:
	def POST(self):
		l.info('POST adduser')
		i = web.input()
		if 'username' not in i:
			l.error('username field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing username')
		if 'password' not in i:
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
		l.debug('Creating new user %s' % username)
		guid = web.d.addUser(username, h.hexdigest())
		if not guid:
			return render.error(web.ctx.fullpath, 'EXISTS', 'username exists')
		return render.index(None)

class logon:
	def GET(self):
		l.info('GET logon')
		return render.logon()
	def POST(self):
		l.info('POST logon')
		i = web.input()
		if 'username' not in i:
			l.error('username field required for POST')
			return logon_redirect()
		if 'password' not in i:
			l.error('password field required for POST')
			return logon_redirect()
		# XXX: validate inputs
		username = str(i['username'])
		password = str(i['password'])
		h = hashlib.sha1()
		# hash password
		h.update(password)
		# hash with salt
		h.update(username)
		(db_guid, db_session) = web.d.getValidUser(username, h.hexdigest())
		if not db_guid:
			# invalid credentials
			return logon_redirect()
		# create cookie
		COOKIE_TTL = 10
		expiration = int(time.time()) + COOKIE_TTL
		cookie = scp.SecureCookie(str(db_guid), expiration, 'mydata', str(db_session))
		# this may produce a slight variation in expiration dates between what we set
		# and what web.py sets, but we really don't care.
		web.setcookie('ctfcookie', cookie.value, COOKIE_TTL, secure=True, httponly=True)
		return render.index(None)
if __name__ == "__main__":
	# run from the same directory as the service file
	os.chdir(rootdir)
	c = config.Configurator()
	c.load(configfile)
	l.__init__(c.log, level=c.lvl)
	try:
		web.d = db.DB(c.db)
	except IOError:
		l.die("Failed to initialize database.")
	try:
		scp.secret_key = c.secret
	except IOError:
		l.die("Failed to initialize secret key.")
	l.info("Starting web service.")
	app = web.application(urls, globals())
	app.run()
