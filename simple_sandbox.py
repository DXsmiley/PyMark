# Turns out that this is actually really, really bad.
# There's many well known ways to escape from it.
# This basiclaly makes sure that people don't accidentaly
# damage your system. However, if they're trying to, 
# it's very easy for them to get around it!

import sys as __sys__hidden__

class IlligalImport(Exception):
	def __init__(self, module_name):
		self.module_name = module_name

	def __str__(self):
		return "You may not import package '{}'.".format(self.module_name)

class IlligalFunctionError(Exception):
	pass

class IlligalFileAccessError(Exception):
	def __init__(self, filename):
		self.filename = filename

	def __str__(self):
		return "You may not open file '{}'.".format(self.filename)

def IlligalFunction(*a, **b):
	raise IlligalFunctionError()

class ImportBlocker():
	def __init__(self, *args):
		self.module_names = args

	def find_module(self, fullname, path = None):
		return self

	def load_module(self, name):
		raise IlligalImport(name)

class OpenBlocker():
	def __init__(self, open_function, allowed_files):
		self.open_function = open_function

	def __call__(self, filename, mode = 'r'):
		if filename in allowed_files:
			return open_function(filename, mode)
		else:
			raise IlligalFileAccessError(filename)

open_blocker = OpenBlocker({SANDBOX_OPEN_FUNCTION}, {SANDBOX_ALLOWED_FILES})

__sys__hidden__.meta_path = [ImportBlocker()]

__blocked_modules__ = [
	'os',
	'sys',
	'sysconfig',
	'__main__',
	'_thread',
	'abc'
]

for i in __blocked_modules__:
	__sys__hidden__.modules[i] = None

__sys__hidden__ = None

open = open_blocker
delattr = IlligalFunction
setattr = IlligalFunction
hasattr = IlligalFunction
eval = IlligalFunction
exec = IlligalFunction
globals = IlligalFunction
locals = IlligalFunction
memoryview = IlligalFunction
vars = IlligalFunction
__import__ = IlligalFunction
__dir__ = IlligalFunction
__builtins__ = None
__loader__ = None


# User code goes here.