#!/usr/bin/env python

# system modules
import hashlib
import os
import sys
import time
import uuid
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
sys.excepthook = exceptions

urls = (
	'/', 'index',
	'/adduser', 'adduser',
	'/logon', 'logon'
)

COOKIE_NAME = 'ctfauth'
COOKIE_TTL = 10

def get_session_info():
	keys = [ 'HTTP_USER_AGENT', 'HTTP_X_FORWARDED_FOR' ]
	values = {}
	for key in keys:
		value = web.ctx.env.get(key, 'NO_' + key)
		values[key] = value
	return values

def get_session_hash():
	values = get_session_info()
	h = hashlib.sha1()
	for value in values:
		h.update(value)
	return h.hexdigest()

def logon_redirect():
	expire_cookie()
	return web.seeother('/logon')

def expire_cookie():
	web.setcookie(COOKIE_NAME, '', -1)

def create_cookie(guid, data, session):
	# this may produce a slight variation in expiration dates between what we set
	# and what web.py sets, but we really don't care.
	expiration = int(time.time()) + COOKIE_TTL
	cookie = scp.SecureCookie(guid, expiration, data, get_session_hash())
	web.setcookie(COOKIE_NAME, cookie.value, COOKIE_TTL, secure=True, httponly=True)

def logged_on():
	cookie_data = web.cookies().get(COOKIE_NAME)
	if cookie_data is None:
		return False
	return scp.is_valid(cookie_data, get_session_hash())

def csrf_token():
	if 'csrf_token' not in session:
		session.csrf_token = uuid.uuid4().hex
	return session.csrf_token

def csrf_protected(f):
	def decorated(*args, **kwargs):
		i = web.input()
		if 'csrf_token' not in i or i.csrf_token != session.pop('csrf_token', None):
			raise web.HTTPError(
					"400 Bad Request",
					{ 'content_type': 'text/html' },
					'''Cross Site Request Forgery detected''')
		return f(*args, **kwargs)
	return decorated

render = web.template.render('templates/', globals={'csrf_token':csrf_token})

##
# @brief index page
class index:
	##
	# @brief generate index
	#
	# @return index.html
	def GET(self):
		l.info('GET index')
		if not logged_on():
			return logon_redirect()
		return render.index(None)

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
		expire_cookie()
		return render.logon()
	@csrf_protected
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
		create_cookie(str(db_guid), '', '')
		return web.seeother('/')

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
	web.config.debug = False
	app = web.application(urls, globals())
	session = web.session.Session(app, web.session.DiskStore('ctf-data/sessions'))
	app.run()
