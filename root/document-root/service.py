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
from recaptcha.client import captcha

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
	'/logon', 'logon',
	'/checkout', 'checkout',
	'/purchase', 'purchase',
)

## Name of authorization cookie
COOKIE_NAME = 'ctfauth'
## Cookie expiration time, in seconds
COOKIE_TTL = 100

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

#
# @brief Create the global authentication cookie using the Secure Cookie Protocol
#
# @param guid The guid representing the user
# @param data Any data we wish to store securely with the user.
def create_cookie(guid, data):
	# this may produce a slight variation in expiration dates between what we set
	# and what web.py sets, but we really don't care.
	expiration = int(time.time()) + COOKIE_TTL
	session.cookie = scp.SecureCookie(get_session_hash(), web.secret)
	serial = session.cookie.serialize(guid, int(time.time()) + COOKIE_TTL, data)
	web.setcookie(COOKIE_NAME, serial, COOKIE_TTL, secure=True, httponly=True)

##
# @brief Determine whether the user is logged onto the system
#
# @return True or False
def logged_on():
	cookie = web.cookies().get(COOKIE_NAME)
	if cookie is None:
		return False
	return session.cookie.isValid(cookie)

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
		books = web.d.getBooks()
		serial = cookie = web.cookies().get(COOKIE_NAME)
		user = session.cookie.getData(serial)
		return render.index(user, books)


##
# @brief Interface for creating users
class adduser:
	def GET(self):
		l.info('GET adduser')
		expire_cookie()
		cap = captcha.displayhtml(web.captcha_public_key, use_ssl=True, error="Something broke.")
		return render.adduser(cap)
	def POST(self):
		l.info('POST adduser')
		i = web.input()
		if 'username' not in i:
			l.error('username field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing username')
		if 'password' not in i:
			l.error('password field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing password')
		if 'password2' not in i:
			l.error('password2 field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing password2')
		if 'recaptcha_challenge_field' not in i:
			l.error('recaptcha_challenge_field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing recaptcha challenge')
		if 'recaptcha_response_field' not in i:
			l.error('recaptcha_response_field required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing recaptcha response')
		# XXX: validate inputs
		username = str(i['username'])
		password = str(i['password'])
		password2 = str(i['password2'])
		if password != password2:
			l.warn("passwords don't match. not creating user.")
			return render.error(web.ctx.fullpath, 'BADREQ', 'password mismatch')
		challenge = i['recaptcha_challenge_field']
		response = i['recaptcha_response_field']
		result = captcha.submit(challenge, response, web.captcha_private_key, web.ctx.ip)
		if result.error_code:
			l.warn('error validating captcha: %s' % result.error_code)
			return render.error(web.ctx.fullpath, 'BADREQ', 'bad captcha: %s' % result.error_code)
		if not result.is_valid:
			l.warn('invalid captcha')
			return render.error(web.ctx.fullpath, 'BADREQ', 'bad captcha')
		h = hashlib.sha1()
		# hash password
		h.update(password)
		# hash with salt
		h.update(username)
		l.debug('Creating new user %s' % username)
		guid = web.d.addUser(username, h.hexdigest())
		if not guid:
			return render.error(web.ctx.fullpath, 'EXISTS', 'username exists')
		create_cookie(str(guid), username)
		return web.seeother('/')
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
		create_cookie(str(db_guid), username)
		return web.seeother('/')

class checkout():
	def GET(self):
		l.info('GET checkout')
		web.seeother('/')
	@csrf_protected
	def POST(self):
		l.info('POST checkout')
		if not logged_on():
			return logon_redirect()
		i = web.input()
		if 'book' not in i:
			l.error('book required for POST')
			return web.seeother('/')
		book = i['book']
		return render.checkout(book)
class purchase():
	def GET(self):
		l.info('GET purchase')
		web.seeother('/')
	@csrf_protected
	def POST(self):
		l.info('POST purchase')
		if not logged_on():
			return logon_redirect()
		i = web.input()
		if  'name' not in i:
			l.error('name required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing name')
		if 'card' not in i:
			l.error('card required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing card')
		if 'ccv' not in i:
			l.error('ccv required for POST')
			return render.error(web.ctx.fullpath, 'BADREQ', 'missing ccv')
		book = 'foo'
		return render.purchase(book)

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
		web.secret = c.secret
	except IOError:
		l.die("Failed to initialize secret key.")
	web.captcha_public_key = c.captcha_public_key
	web.captcha_private_key = c.captcha_private_key
	if not web.captcha_public_key:
		l.critical("SECURITY ERROR: Could not get captcha public key")
	if not web.captcha_private_key:
		l.critical("SECURITY ERROR: Could not get captcha private key")
	l.info("Starting web service.")
	web.config.debug = False
	app = web.application(urls, globals())
	session = web.session.Session(app, web.session.DiskStore('ctf-data/sessions'))
	app.run()
