import os
import json

# Settings are initially loaded from settings.json.
# Settings not found in the file are then loaded
# from system environment variables.
# Note that all environment variables start with
# 'pymark_', although the properties in the file
# should not.

# It is also possible to assign a value to any
# environment variable indirectly. For example,
# on Heroku, you need to use the PORT envrinment
# variable, not anything else. You can set
# pymark_port to ENV:PORT to acheive this.

settings = {}

try:
	with open('./settings.json') as f:
		j = json.loads(f.read())
		settings = j
except FileNotFoundError:
	pass

def load_setting(name, default = None):
	if name not in settings:
		settings[name] = os.environ.get('pymark_' + name, default)
	v = settings[name]
	if v.startswith("ENV:"):
		settings[name] = os.environ.get(v[4:], default)

load_setting('invoke_code', 'python {}')
load_setting('invoke_shell', 0)
load_setting('db_login')
load_setting('db_name', 'database')
load_setting('port', 8080)



def get(name):
	return settings[name]