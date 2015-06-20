# Turns out that this is actually really, really bad.
# There's many well known ways to escape from it.
# This basiclaly makes sure that people don't accidentaly
# damage your system. However, if they're trying to, 
# it's very easy for them to get around it!

import sys as __sys__hidden__

class ImportBlocker(object):
	def __init__(self, *args):
		self.module_names = args

	def find_module(self, fullname, path = None):
		return self

	def load_module(self, name):
		raise IlligalImport("You may not import package '{}'.".format(name))

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

class IlligalImport(Exception):
	pass

class IlligalFunctionError(Exception):
	pass

def IlligalFunction(*a, **b):
	raise IlligalFunctionError()

open = IlligalFunction
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