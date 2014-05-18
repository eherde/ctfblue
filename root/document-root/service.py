#!/usr/bin/env python
## @package service
# The web service

# system modules
import hashlib
import os
import sys
import time
import uuid
import web

## The directory where the project is run from
rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))

## Make sure that the service can find its libraries
sys.path.append(os.path.join(rootdir, 'lib'))

# local modules
import config
import db
import scp
from log import l, exceptions
import captcha

## Set the path to our configuration
configfile = os.path.join('ctf-data/ctf.yaml')
# Set a hook to log uncaught exceptions
sys.excepthook = exceptions

## Mapping from url => class
urls = (
	'/', 'index',
	'/adduser', 'adduser',
	'/logon', 'logon'
)

## Name of authorization cookie
COOKIE_NAME = 'ctfauth'
## Cookie expiration time, in seconds
COOKIE_TTL = 10

##
# @brief get information specific to this session.
# This information should not change over the duration of a session.
#
# @return dictionary of http information that we care about
def get_session_info():
	keys = [ 'HTTP_USER_AGENT', 'HTTP_X_FORWARDED_FOR' ]
	values = {}
	for key in keys:
		value = web.ctx.env.get(key, 'NO_' + key)
		values[key] = value
	return values

##
# @brief Hash the all values of session information into a single string
#
# @return 40 character string that is the hash of HTTP session information
def get_session_hash():
	values = get_session_info()
	h = hashlib.sha1()
	for value in values:
		h.update(value)
	return h.hexdigest()

##
# @brief redirect the user to the logon page.
#
# @return returns the logon page
def logon_redirect():
	return web.seeother('/logon')

##
# @brief Expire the authentication cookie. This is done by setting the timeout to -1
def expire_cookie():
	web.setcookie(COOKIE_NAME, '', -1)

##
# @brief Create the global authentication cookie using the Secure Cookie Protocol
#
# @param guid The guid representing the user
# @param data Any data we wish to store securely with the user.
# @param session Information that should not change within a session.
def create_cookie(guid, data, session):
	# this may produce a slight variation in expiration dates between what we set
	# and what web.py sets, but we really don't care.
	expiration = int(time.time()) + COOKIE_TTL
	cookie = scp.SecureCookie(guid, expiration, data, get_session_hash())
	web.setcookie(COOKIE_NAME, cookie.value, COOKIE_TTL, secure=True, httponly=True)

##
# @brief Determine whether the user is logged onto the system
#
# @return True or False
def logged_on():
	cookie_data = web.cookies().get(COOKIE_NAME)
	if cookie_data is None:
		return False
	return scp.is_valid(cookie_data, get_session_hash())

##
# @brief Get the global csrf token, creating it if it does not exist
#
# @return the hex value of the guid
def csrf_token():
	if 'csrf_token' not in session:
		session.csrf_token = uuid.uuid4().hex
	return session.csrf_token

##
# @brief decorator for protecting requests for forgery
#
# @param f The function to decorate
#
# @return  The decorated function
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

##
# @brief The rendering engine, updated with the directory we care about
# and the csrf token. This allows templates to reference the csrf token.
render = web.template.render('templates/', globals={'csrf_token':csrf_token})

##
# @brief index page
class index:
	##
	# @brief generate index
	#
	# @return the index page.
	def GET(self):
		l.info('GET index')
		if not logged_on():
			return logon_redirect()
		return render.index(None)

##
# @brief Interface for creating users
class adduser:
	def GET(self):
		l.info('GET adduser')
		expire_cookie()
		return render.adduser()
	def POST(self):
		l.info('POST adduser')
		i = web.input()
		if 'username' not in i:
			l.error('username field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing username')
		if 'password' not in i:
			l.error('password field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing password')
		if 'recaptcha_challenge_field' not in i:
			l.error('recaptcha_challenge_field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing recaptcha_challenge_field')
		if 'recaptcha_response_field' not in i:
			l.error('recaptcha_response_field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'recaptcha_response_field')
		recaptcha_challenge_field = str(i['recaptcha_challenge_field'])
		recaptcha_response_field = str(i['recaptcha_response_field'])
		l.info(recaptcha_challenge_field)
		l.info(recaptcha_response_field)
		response = captcha.submit(recaptcha_challenge_field,recaptcha_response_field,'6LdFkvMSAAAAANE5KvuYd7_7uC1H6mYZ1RZeofM0','192.168.33.235')
		l.info(response.is_valid)
		if not response.is_valid:
			l.info('false captcha')
			return render.error(web.ctx.fullpath, 'NOTHUMAN', 'wrong captcha value')
		else:
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

##
# @brief Interface for logging onto the service
class logon:
	##
	# @brief ensures that the user is not logged on and presents the user
	# with the logon page.
	#
	# @return the logon page
	def GET(self):
		l.info('GET logon')
		expire_cookie()
		return render.logon()
	##
	# @brief attempts to logon to receive an authentication cookie
	#
	# @return the index page on success, logon page on failure
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
