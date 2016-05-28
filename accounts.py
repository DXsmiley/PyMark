import json
import random
import hashlib
import time
import databases
import cryptorand

# The time for a session to become invalid, in seconds.
# This is by default 3 hours. (3 * 60 * 60)
session_timeout = 3 * 60 * 60

class ErrorBase(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
	def message(self):
		return str(self.value)

class ErrorInvalidLogin(ErrorBase): pass
class ErrorAccountExists(ErrorBase): pass
class ErrorInvalidPassword(ErrorBase): pass
class ErrorInvalidUsername(ErrorBase): pass

def hash(x):
	return hashlib.sha224(str.encode(x)).hexdigest()

def make_salt():
	return str(cryptorand.generate(8))

def check_username(s):
	if len(s) < 4:
		raise ErrorInvalidUsername('Username must be at least 4 characters long.')
	if len(s) > 20:
		raise ErrorInvalidUsername('Username must not have more than 20 characters.')
	if not s.isalnum():
		raise ErrorInvalidUsername('Username must only have numbers and letters.')

def check_password(s):
	if len(s) < 4:
		raise ErrorInvalidPassword('Password must be longer than 4 characters.')

def login(username, password):
	username = username.lower()
	u_doc = databases.c_accounts.find_one({'_id': username})
	if u_doc == None:
		raise ErrorInvalidLogin('User does not exist.')
	pass_salted = password + u_doc['salt']
	pass_hashed = hash(pass_salted)
	if u_doc['password'] != pass_hashed:
		raise ErrorInvalidLogin('Password is incorrect.')
	session_id = str(cryptorand.generate(8))
	session_key = str(cryptorand.generate(8))
	sessions_doc = {
		'_id': session_id,
		'key': session_key,
		'user': username,
		'time': time.time(),
	}
	databases.c_sessions.insert(sessions_doc)
	return (session_id, session_key)

def create(username, password):
	username = username.lower()
	check_username(username)
	check_password(password)
	if databases.c_accounts.find_one({'_id': username}) != None:
		raise ErrorAccountExists('An account with that username already exists.')
	salt = make_salt()
	pass_hashed = hash(password + salt)
	document = {
		'_id': username,
		'salt': salt,
		'password': pass_hashed
	}
	databases.c_accounts.insert(document)
	return login(username, password)

# Sessions currently don't care about time.
# This needs to be fixed.
def session_check(session_id, session_key):
	s_doc = databases.c_sessions.find_one({'_id': session_id})
	valid = s_doc != None and s_doc['key'] == session_key and time.time() - s_doc['time'] < session_timeout
	if not valid:
		databases.c_sessions.remove({'_id': session_id})
	return valid

def session_get_username(session_id):
	return databases.c_sessions.find_one({'_id': session_id})['user']

def session_get_account_data(session_id):
	username = session_get_username(session_id)
	return get_account_data(username)

def get_account_data(username):
	return databases.c_accounts.find_one({'_id': username})

def list_accounts(show_invisible = False):
	l = []
	for i in databases.c_accounts.find():
		if i.get('visible', True) or show_invisible:
			l.append(i['_id'])
	return l
