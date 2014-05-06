## @package db
# Database access interface
#
# Commands for writing information to the database

# system modules
import uuid
import os
import sqlite3
import sys
import unittest

# local modules
from log import l

sys.dont_write_byte_code = True

class DB:
	def __init__(self, path):
		if not os.path.exists(path) and path != ':memory:':
			l.error("Database %s does not exist, cannot connect." % path)
			raise IOError
		self.con = sqlite3.connect(path)
		self.xec = self.con.cursor()

	def addUser(self, username, password):
		statement = 'INSERT INTO Users VALUES (?, ?, ?, ?)'
		# The guid will be stored in the cookie with the user.
		# The session_id will be used to simulate an SSL ID.
		guid = str(uuid.uuid4())
		session_id = str(uuid.uuid4())
		entry = ( guid, username, password, session_id, )
		self.xec.execute(statement, entry)
		self.con.commit()
		return guid
	def getUser(self, guid):
		statement = 'SELECT Username, Password, SessionID FROM Users WHERE GUID = ?'
		entry = ( guid, )
		return self.xec.execute(statement, entry).fetchone()
	def setSessionID(self, guid, session_id):
		statement = 'UPDATE Users SET SessionID = ? WHERE GUID = ?'
		entry = ( session_id, guid, )
		self.xec.execute(statement, entry)
		self.con.commit()

testdb = ':memory:'
testuser = 'MyUser'
testpass = 'MyPass'
testsession = 12345

class TestDB(unittest.TestCase):
	def setUp(self):
		self.db = DB(testdb)
		self.db.xec.execute("CREATE TABLE Users(GUID, Username, Password, SessionID)")
		self.db.con.commit()
	def tearDown(self):
		self.db.con.close()
	def test_addUser(self):
		self.db.addUser(testuser, testpass)
	def test_getUser(self):
		guid = self.db.addUser(testuser, testpass)
		(username, password, session_id) = self.db.getUser(guid)
	def test_setSessionID(self):
		guid = self.db.addUser(testuser, testpass)
		self.db.setSessionID(guid, testsession)
		(username, password, session_id) = self.db.getUser(guid)
		self.assertTrue(session_id == testsession)

if __name__ == '__main__':
	# run from the same directory as the module
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	sys.exit(unittest.main(verbosity=2))
