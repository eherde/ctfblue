## @package db
# Database access interface
#
# Commands for writing information to the database
#
# This module enforces strict rules regarding inputs to the database.
# The below describes the rules for each database field.
#
# - Users.GUID		=> string, exactly 36 characters
# - Users.Username	=> string, 32 character max
# - Users.Password	=> string, exactly 40 characters

# system modules
import os
import re
import sqlite3
import sys
import unittest
import uuid
import web

# local modules
from log import l

sys.dont_write_byte_code = True

USERNAME_MAX = 32

HEXCHARS='[a-f0-9]'
RE_UUID = re.compile('^%s{8}-%s{4}-%s{4}-%s{4}-%s{12}$' % (HEXCHARS, HEXCHARS, HEXCHARS, HEXCHARS, HEXCHARS))
RE_SHA1 = re.compile('^%s{40}$' % HEXCHARS)

##
# @brief Database Interface
class DB:
	##
	# @brief Create a new connection to the database
	#
	# @param path path to the database file
	#
	# @return new DB object.
	def __init__(self, path):
		if not os.path.exists(path) and path != ':memory:':
			l.critical("Database %s does not exist, cannot connect." % path)
			raise IOError
		self.xec = web.database(dbn='sqlite', db=path)
		# Prevent web.db from printing queries
		self.xec.printing = False
	##
	# @brief Add a new user to the database
	#
	# @param username the username
	# @param password the 40 character password hash
	#
	# @return guid associated with this user
	def addUser(self, username, password):
		if type(username) is not str:
			l.error("username type is not str.")
			return None
		if type(password) is not str:
			l.error("password type is not str.")
			return None
		if len(username) > USERNAME_MAX:
			l.error('username is greater than %d characters.' % USERNAME_MAX)
			return None
		if not RE_SHA1.match(password):
			l.error("%s does not match regular expression '%s'." % (password, RE_SHA1.pattern))
			return None
		# The guid will be stored in the cookie with the user.
		guid = str(uuid.uuid4())
		try:
			self.xec.insert('Users', GUID=guid, Username=username, Password=password)
		except sqlite3.IntegrityError:
			l.warn("username %s already exists." % username)
			return None
		return guid
	# @brief get all books in the table
	#
	# @return iterable of all books
	def getBooks(self):
		return self.xec.select('Books', what='*')
	##
	# @brief lookup the price of a book
	#
	# @param book the full name of the book
	#
	# @return the price of the book
	def getPrice(self, book):
		where = dict(Name=book)
		res = self.xec.select('Books', what='Price', where=web.db.sqlwhere(where))
		try:
			return res[0].Price
		except IndexError:
			l.warn('No entry for %s' % book)
		except AttributeError:
			l.critical('BUG: no attribute Price')
	##
	# @brief Get entries associated with a user by username
	#
	# @param username 32 character max string
	#
	# @return tuple (Username, Password)
	def getUser(self, username):
		if type(username) is not str:
			l.error("username type is not str")
			return ( None, None, )
		if len(username) > USERNAME_MAX:
			l.error("%s is greater than %d characters." % (username, USERNAME_MAX))
			return ( None, None, )
		where = dict(Username=username)
		res = self.xec.select('Users', what='GUID,Password', where=web.db.sqlwhere(where))
		try:
			res = res[0]
		except IndexError:
			# This username did not exist, return the correct type
			l.warn("username %s does not exist." % username)
			return ( None, None, )
		return (res.GUID, res.Password)
	##
	# @brief Get entries associated with a user by guid
	#
	# @param guid 36 character guid string
	#
	# @return tuple (Username, Password)
	def getUserG(self, guid):
		if type(guid) is not str:
			l.error("guid type is not str")
			return ( None, None, )
		if not RE_UUID.match(guid):
			l.error("%s does not match regular expression '%s'." % (guid, RE_UUID.pattern))
			return ( None, None, )
		where = dict(GUID=guid)
		res = self.xec.select('Users', what='Username,Password', where=web.db.sqlwhere(where))
		try:
			res = res[0]
		except IndexError:
			# This guid did not exist, return the correct type
			l.warn("guid %s does not exist." % guid)
			return ( None, None, )
		return (res.Username, res.Password)
	##
	# @brief Get entries associated with a user by guid
	#
	# @param guid 36 character guid string
	#
	# @return tuple (Username, Password)
	def getValidUser(self, username, password):
		if type(username) is not str:
			l.error("username type is not str")
			return None
		if len(username) > USERNAME_MAX:
			l.error("%s is more that %d characters." % (username, USERNAME_MAX))
			return None
		if type(password) is not str:
			l.error("password type is not str")
			return None
		if not RE_SHA1.match(password):
			l.error("%s does not match regular expression '%s'." % (password, RE_SHA1.pattern))
			return None
		where = dict(Username=username, Password=password)
		res = self.xec.select('Users', what='GUID', where=web.db.sqlwhere(where))
		try:
			res = res[0]
		except IndexError:
			# This guid did not exist, return the correct type
			l.warn("Bad password match for user %s" % username)
			return None
		return res.GUID

testdb = ':memory:'
testuser = 'MyUser'
testpass = '1234567890abcdef098712345678900987654321'

class TestDB(unittest.TestCase):
	def setUp(self):
		self.db = DB(testdb)
		self.db.xec.query("CREATE TABLE Users(GUID, Username UNIQUE, Password)")
		self.db.xec.query("CREATE TABLE Books(Name, Price)")
		self.db.xec.query('INSERT INTO Books VALUES ("Secure Electronic Commerce", 27.50)')
	def test_init(self):
		# Initialization is already tested in setup
		# This is a necessary evil if we are going to keep the database in memory
		pass
	def test_init_neg(self):
		self.assertRaises(IOError, DB, '')
	def test_addUser(self):
		guid = self.db.addUser(testuser, testpass)
		self.assertFalse(guid is None)
	def test_addUser_neg_nouser(self):
		self.assertEqual(self.db.addUser(None, testpass), None)
	def test_addUser_neg_nopass(self):
		self.assertEqual(self.db.addUser(testuser, None), None)
	def test_addUser_neg_userlong(self):
		self.assertEqual(self.db.addUser('1234567890abcdefghij1234567890123', testpass), None)
	def test_addUser_neg_passbadregex(self):
		self.assertEqual(self.db.addUser(testuser, 'abcdefg'), None)
	def test_addUser_neg_userexists(self):
		self.assertNotEqual(self.db.addUser(testuser, testpass), None)
		self.assertEqual(self.db.addUser(testuser, testpass), None)
	def test_getBooks(self):
		res = self.db.getBooks()
		self.assertFalse(res is None)
	def test_getPrice(self):
		res = self.db.getPrice('Secure Electronic Commerce')
		self.assertEqual(res, 27.50)
	def test_getPrice_neg_nobook(self):
		res = self.db.getPrice('Not a Book')
		self.assertTrue(res is None)
	def test_getUser(self):
		guid = self.db.addUser(testuser, testpass)
		self.assertFalse(guid is None)
		self.assertNotEqual(self.db.getUser(testuser), ( None, None, ))
	def test_getUser_neg_none(self):
		self.assertEqual(self.db.getUser(None), ( None, None, ))
	def test_getUser_neg_badstr(self):
		self.assertEqual(self.db.getUser(''), ( None, None, ))
	def test_getUser_neg_notexist(self):
		self.assertEqual(self.db.getUser(testuser), ( None, None, ))
	def test_getUserG(self):
		guid = self.db.addUser(testuser, testpass)
		self.assertFalse(guid is None)
		self.assertNotEqual(self.db.getUserG(guid), ( None, None, ))
	def test_getUserG_neg_none(self):
		self.assertEqual(self.db.getUserG(None), ( None, None, ))
	def test_getUserG_neg_guidbadregex(self):
		self.assertEqual(self.db.getUserG('abcdefg'), ( None, None, ))
	def test_getValidUser(self):
		guid = self.db.addUser(testuser, testpass)
		self.assertFalse(guid is None)
		self.assertNotEqual(self.db.getValidUser(testuser, testpass), None)
	def test_getValidUser_neg_usrnone(self):
		self.assertEqual(self.db.getValidUser(None, testpass), None)
	def test_getValidUser_neg_passnone(self):
		self.assertEqual(self.db.getValidUser(testuser, None), None)
	def test_getValidUser_neg_badusr(self):
		self.assertEqual(self.db.getValidUser('1234567890abcdefghij123457890123', testpass), None)
	def test_getValidUser_neg_badpass(self):
		self.assertEqual(self.db.getValidUser(testuser, 'abcdefg'), None)
	def test_getValidUser_neg_nomatch(self):
		self.assertEqual(self.db.getValidUser(testuser, testpass), None)

if __name__ == '__main__':
	import logging
	# suppress logging for unit tests
	logging.disable(logging.CRITICAL)
	# run from the same directory as the module
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	sys.exit(unittest.main(verbosity=2))
