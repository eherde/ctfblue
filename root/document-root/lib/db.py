## @package db
# Database access interface
#
# Commands for writing information to the database
#
# This module enforces string rules regarding inputs to the database.
# The below describes the rules for each database field.
#
# - Users.GUID		=> string, exactly 36 characters
# - Users.Username	=> string, 32 character max
# - Users.Password	=> string, exactly 40 characters
# - Users.SessionID	=> string, exactly 36 characters

# system modules
import os
import re
import sqlite3
import sys
import unittest
import uuid

# local modules
from log import l

sys.dont_write_byte_code = True

USERNAME_MAX = 32
SESSION_ID_LEN = 36
NULL_SESSION_ID = '00000000-0000-0000-0000-000000000000'

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
		self.con = sqlite3.connect(path)
		self.xec = self.con.cursor()
	##
	# @brief Add a new user to the database
	#
	# @param username the username
	# @param password the 20 character password hash
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
		statement = 'INSERT INTO Users VALUES (?, ?, ?, ?)'
		# The guid will be stored in the cookie with the user.
		guid = str(uuid.uuid4())
		# The session_id will be used to simulate an SSL ID.
		session_id = str(uuid.uuid4())
		entry = ( guid, username, password, session_id, )
		try:
			self.xec.execute(statement, entry)
		except sqlite3.IntegrityError:
			l.warn("username %s already exists." % username)
			return None
		self.con.commit()
		return guid
	##
	# @brief clear the Session ID for a user. should be performed on logout.
	#
	# @param guid 36 character guid string
	#
	# @return True or False
	def clearSessionID(self, guid):
		return self.setSessionID(guid, NULL_SESSION_ID)
	##
	# @brief Get entries associated with a user by guid
	#
	# @param guid 36 character guid string
	#
	# @return tuple (Username, Password, SessionID)
	def getUser(self, guid):
		if type(guid) is not str:
			l.error("guid type is not str")
			return ( None, None, None, )
		if not RE_UUID.match(guid):
			l.error("%s does not match regular expression '%s'." % (guid, RE_UUID.pattern))
			return ( None, None, None, )
		statement = 'SELECT Username, Password, SessionID FROM Users WHERE GUID = ?'
		entry = ( guid, )
		res = self.xec.execute(statement, entry).fetchone()
		# This guid did not exist, return the correct type
		if res is None:
			l.warn("guid %s does not exist." % guid)
			return ( None, None, None, )
		return res
	##
	# @brief Set the session id of a user by guid
	#
	# @param guid 36 character guid string
	# @param session_id the new session id
	#
	# @return True or False
	def setSessionID(self, guid, session_id):
		if type(guid) is not str:
			l.error("guid type is not str")
			return False
		if type(session_id) is not str:
			l.error("session_id type is not str")
			return False
		if not RE_UUID.match(guid):
			l.error("%s does not match regular expression '%s'." % (guid, RE_UUID.pattern))
			return False
		if len(session_id) != SESSION_ID_LEN:
			l.error("session_id is not %d characters." % SESSION_ID_LEN)
		statement = 'UPDATE Users SET SessionID = ? WHERE GUID = ?'
		entry = ( session_id, guid, )
		self.xec.execute(statement, entry)
		# if the rowcount is 1, update succeeded
		if self.xec.rowcount != 1:
			l.warn("guid %s does not exist." % guid)
			return False
		self.con.commit()
		return True

testdb = ':memory:'
testuser = 'MyUser'
testpass = '1234567890abcdef098712345678900987654321'
testsession = '12345678-abcd-abcd-1234-1234567890ab'

class TestDB(unittest.TestCase):
	def setUp(self):
		self.db = DB(testdb)
		self.db.xec.execute("CREATE TABLE Users(GUID, Username UNIQUE, Password, SessionID)")
		self.db.con.commit()
	def tearDown(self):
		self.db.con.close()
	def test_init(self):
		# Initialization is already tested in setup
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
	def test_getUser(self):
		guid = self.db.addUser(testuser, testpass)
		self.assertFalse(guid is None)
		(username, password, session_id) = self.db.getUser(guid)
	def test_getUser_neg_none(self):
		self.assertEqual(self.db.getUser(None), ( None, None, None, ))
	def test_getUser_neg_guidbadregex(self):
		self.assertEqual(self.db.getUser('abcdefg'), ( None, None, None, ))
	def test_getUser_neg_notexist(self):
		self.assertEqual(self.db.getUser(testsession), ( None, None, None, ))
	def test_clearSessionID(self):
		guid = self.db.addUser(testuser, testpass)
		self.assertFalse(guid is None)
		self.assertTrue(self.db.clearSessionID(guid))
		(username, password, session_id) = self.db.getUser(guid)
		self.assertNotEqual(( username, password, session_id, ), ( None, None, None, ))
		self.assertTrue(session_id == NULL_SESSION_ID)
	def test_setSessionID(self):
		guid = self.db.addUser(testuser, testpass)
		self.assertFalse(guid is None)
		self.assertTrue(self.db.setSessionID(guid, testsession))
		(username, password, session_id) = self.db.getUser(guid)
		self.assertNotEqual(( username, password, session_id, ), ( None, None, None, ))
		self.assertTrue(session_id == testsession)
	def test_setSessionID_neg_noguid(self):
		self.assertFalse(self.db.setSessionID(None, testsession))
	def test_setSessionID_neg_nosession(self):
		self.assertFalse(self.db.setSessionID(testsession, None))
	def test_setSessionID_neg_guidbadrexeg(self):
		self.assertFalse(self.db.setSessionID('abcdefg', testsession))
	def test_setSessionID_neg_badsessionlen(self):
		self.assertFalse(self.db.setSessionID(testsession, 'abcdefg123456'))
	def test_setSessionID_neg_guidnotexist(self):
		self.assertFalse(self.db.setSessionID(testsession, testsession))

if __name__ == '__main__':
	import logging
	# suppress logging for unit tests
	logging.disable(logging.CRITICAL)
	# run from the same directory as the module
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	sys.exit(unittest.main(verbosity=2))
