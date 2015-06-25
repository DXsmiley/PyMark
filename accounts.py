import json
import random
import hashlib
import time

# Accounts are currently salted and hashed. It might be a better idea to
# store them as plaintext in case anyone forgets their password or something.

database = dict()
sessions = dict()

session_id_counter = 0

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

def load():
	global database
	global sessions
	global session_id_counter
	try:
		with open('accounts.json') as f:
			database = json.loads(f.read())
	except FileNotFoundError:
		print('No accounts.json file found. One will be created automatically.')
	try:
		with open('sessions.json') as f:
			sessions = json.loads(f.read())
		session_id_counter = int(sessions.get('num sessions', 0))
	except FileNotFoundError:
		print('No sessions.json file found. One will be created automatically.')

def save():
	with open('accounts.json', 'w') as f:
		f.write(json.dumps(database))
	sessions['num sessions'] = session_id_counter
	with open('sessions.json', 'w') as f:
		f.write(json.dumps(sessions))

# Reasonable hash, I think.
def hash(x):
	return hashlib.sha224(str.encode(x)).hexdigest()

# Not a very good salt
def make_salt():
	return str(random.randint(0, 2 ** 128))

def login(username, password):
	global session_id_counter
	username = username.lower()
	if username not in database:
		raise ErrorInvalidLogin('User does not exist.')
	pass_salted = password + database[username]['salt']
	pass_hashed = hash(pass_salted)
	if database[username]['password'] != pass_hashed:
		raise ErrorInvalidLogin('Password is incorrect.')
	session_id_counter += 1
	session_id = str(session_id_counter)
	session_key = str(random.randint(0, 2 ** 128))
	sessions[session_id] = {
		'key': session_key,
		'user': username,
		'time': time.time()
	}
	save()
	return (session_id, session_key)

def checkUsername(s):
	if len(s) < 4:
		raise ErrorInvalidUsername('Username must be at least 4 characters long.')
	if len(s) > 20:
		raise ErrorInvalidUsername('Username must not have more than 20 characters.')
	if not s.isalnum():
		raise ErrorInvalidUsername('Username must only have numbers and letters.')

def checkPassword(s):
	if len(s) < 4:
		raise ErrorInvalidPassword('Password must be longer than 4 characters.')

def create(username, password):
	checkUsername(username)
	checkPassword(password)
	username = username.lower()
	if username in database:
		raise ErrorAccountExists('An account with that username already exists.')
	database[username] = dict()
	salt = make_salt()
	database[username]['salt'] = salt
	pass_hashed = hash(password + salt)
	database[username]['password'] = pass_hashed
	save() # Save everything! Not sure if this is the best strategy though.
	return login(username, password)

def session_validate_time(session_id):
	if session_id in sessions:
		if time.time() - sessions[session_id].get('time', 0) > session_timeout:
			del sessions[session_id]

def session_check(session_id, session_key):
	is_valid = False
	session_validate_time(session_id)
	if session_id in sessions:
		if sessions[session_id].get('key', '') == session_key:
			sessions[session_id]['time'] = time.time() # Refresh time
			is_valid = True
	return is_valid

def session_get_username(session_id):
	return sessions[session_id]['user']

def session_get_account_data(session_id):
	return database[session_get_username(session_id)]

def get_account_data(username):
	return database.get(username)

def list_accounts(show_invisible = False):
	return [i for i in database if database[i].get('visible', True) or show_invisible]