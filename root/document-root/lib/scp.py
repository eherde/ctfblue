## @package scp
# Secure Cookie Protocol implementation
#
# See the white paper for details:
# http://www.cse.msu.edu/~alexliu/publications/Cookie/cookie.pdf

# system modules
import hashlib
import hmac
import os
import struct
import sys
import time
import unittest
from Crypto.Cipher import AES

# local modules
from log import l

sys.dont_write_byte_code = True

# format specifiers for packing and unpacking cookie data
USER_FMT = '32s'
EXPR_FMT = 'q'
DATA_FMT = '256s'
SESS_FMT = 'q'
DGST_FMT = '20s'

secret_key = None

def str_to_hex(s):
	return ':'.join(x.encode('hex') for x in s)

def generate_secret():
	return os.urandom(16)

def create_secret_file(path):
	s = generate_secret()
	f = open(path, 'w')
	f.write(s)
	f.close()

def get_secret(path):
	f = open(path, 'r')
	s = f.read()
	f.close()
	return s

##
# @brief compute a Key-Hashed Message Authentication Code
#
# @param msg the message as arbitrary bytes
# @param secret the key as arbitrary bytes
#
# @return 20 byte digest
def HMAC(msg, secret):
	h = hmac.new(secret, digestmod=hashlib.sha1)
	for i in range(100):
		h.update(msg)
	return h.digest()


def hashk(user, expiration, secret):
	msg = struct.pack(USER_FMT + EXPR_FMT, user, expiration)
	return HMAC(msg, secret)

def hashd(user, expiration, data, session, key):
	msg = struct.pack(USER_FMT + EXPR_FMT + DATA_FMT + SESS_FMT,
			user, expiration, data, session)
	return HMAC(msg, key)

def encrypt(msg, key, iv):
	# TODO: validate inputs
	crypter = AES.new(key, AES.MODE_CBC, iv)
	return crypter.encrypt(msg)
def decrypt(msg, key, iv):
	# TODO: validate inputs
	crypter = AES.new(key, AES.MODE_CBC, iv)
	return crypter.decrypt(msg)

class SecureCookie:
	def __init__(self, user, exp, data, session):
		if not secret_key:
			l.error("Failed to instantiate %s: "
					"No secret key initialized."
					% self.__class__.__name__)
			return None
		hash_key = hashk(user, exp, secret_key)
		hashed_data = hashd(user, exp, data, session, str(hash_key))
		s = hashlib.sha1()
		s.update(str(session))
		i_vec = s.digest()[:16]
		ciphertext = encrypt(data.ljust(256, '\0'), str(hash_key)[:16], i_vec)
		self.value = struct.pack(USER_FMT + EXPR_FMT + DATA_FMT + DGST_FMT,
				user, exp, ciphertext, hashed_data)
	def isValid(self, session):
		if not secret_key:
			l.error("Cannot validate cookie. Secret key uninitialized.")
		unpacked = struct.unpack(USER_FMT + EXPR_FMT + DATA_FMT + DGST_FMT, self.value)
		if len(unpacked) != 4:
			l.error("Failed to unpack cookie data.")
		user = unpacked[0]
		exp = unpacked[1]
		ciphertext = unpacked[2]
		hashed_data = unpacked[3]
		hash_key = hashk(user, exp, secret_key)
		s = hashlib.sha1()
		s.update(str(session))
		i_vec = s.digest()[:16]
		plaintext = decrypt(ciphertext.ljust(256,'\0'), str(hash_key)[:16], i_vec)
		verified_hash = hashd(user, exp, plaintext, session, str(hash_key))
		if hashed_data == verified_hash:
			return True
		else:
			return False
# Values for testing
USER = 'mytestuser'
EXPIRATION = time.time()
DATA = 'mytestdata'
SESSION = 12345

class TestSecureCookie(unittest.TestCase):
	def setUp(self):
		global secret_key
		secret_key = generate_secret()
	def test_init(self):
		self.assertTrue(SecureCookie(USER, EXPIRATION, DATA, SESSION))
	def test_verify(self):
		cookie = SecureCookie(USER, EXPIRATION, DATA, SESSION)
		self.assertTrue(cookie)
		self.assertTrue(cookie.isValid(SESSION))

if __name__ == "__main__":
	# run from the same directory as the module
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	sys.exit(unittest.main(verbosity=2))
