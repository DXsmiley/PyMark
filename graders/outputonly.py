from graders.basegrader import BaseGrader
import subprocess
import os
import json
import runcode
import cgi

# This is the simplest code marker.
# It compares the output of the code to the contents of a file.
# If they match, the code scores 100, or 0 otherwise.
# Leading and trailing whitespace is ignored.

# By deafult, this is case sensitive, however you can turn this off with the grader settings.
# 	"case sensitive": False

sandbox_code = """
import sys as __sys__hidden__

class ImportBlocker(object):
	def __init__(self, *args):
		self.module_names = args

	def find_module(self, fullname, path = None):
		return self

	def load_module(self, name):
		raise ImportError("You may not import package '{}'.".format(name))

__sys__hidden__.meta_path = [ImportBlocker()]
__sys__hidden__.modules['os'] = None
__sys__hidden__.modules['sys'] = None

__sys__hidden__ = None

class IlligalFunctionError(Exception):
	pass

def IlligalFunction(*a, **b):
	raise IlligalFunctionError()

open = IlligalFunction
delattr = IlligalFunction
setattr = IlligalFunction
eval = IlligalFunction
exec = IlligalFunction
globals = IlligalFunction
hasattr = IlligalFunction
locals = IlligalFunction
memoryview = IlligalFunction
vars = IlligalFunction
__import__ = IlligalFunction
__builtins__ = None

___input_strings___ = ___INJECTION_LOCATION___
___input_position___ = 0

def input(*args):
	global ___input_position___
	global ___input_strings___
	___input_position___ += 1
	return ___input_strings___[___input_position___ - 1]

"""

# This is the path that should be used 
CODE_PATH = './rundir/code.py'

class Grader(BaseGrader):

	def __init__(self):
		self.test_cases = []
		self.case_sensitive = True
		self.run_timeout = 3

	def preload(self, directory, settings = None):
		self.test_cases = json.loads(open(directory + "cases.json").read())
		if settings != None:
			self.case_sensitive = settings.get("case sensitive", True)
			self.run_timeout = settings.get('timeout', 3)

	def cleanup(self, directory):
		os.remove(CODE_PATH)

	def evaluate(self, code, verbose = False):
		code = sandbox_code + code
		score = 0
		total_weight = 0
		details_string = ''
		# The cases aren't sorted yet though...
		# sorted_cases = [(group, cases) for group, cases in self.test_cases.items()]
		# sorted_cases.sort(key = lambda x: x[1].get('order', 0))
		for group, cases in self.test_cases.items():
			# print('    ' + group)
			details_string += '<h2>' + group + '</h2>\n'
			for k in cases:
				# print('case...')
				weight = k.get('Score', 100)
				# added option for lower case parameter names. this makes things more consistent.
				show_output_details = k.get('Show Result', False) or k.get('show result', False)
				e_input = k['Input'] if 'Input' in k else k['input']
				e_output = k['Output'] if 'Output' in k else k['output']
				is_correct, status, c_output = self.runTestCase(code,
					e_input, e_output, verbose = verbose, show_output_details = show_output_details)
				# print(is_correct)
				if is_correct:
					score += weight
				if show_output_details:
					details_string += '<h3>{}</h3>\n'.format(status)
					details_string += '<p>Your code was given the following input:</p>'
					details_string += '<pre>{}</pre>'.format(cgi.escape('\n'.join(e_input)))
					if is_correct:
						details_string += '<p>Your code produced the following <i>correct</i> output:</p>'
						details_string += '<pre>{}</pre>'.format(cgi.escape('\n'.join(e_output)))
					else:
						details_string += '<p>Your code output the following:</p>'
						details_string += '<pre>{}</pre>'.format(cgi.escape('\n'.join(c_output)))
						details_string += '<p>It should have produced the following:</p>'
						details_string += '<pre>{}</pre>'.format(cgi.escape('\n'.join(e_output)))
				else:
					details_string += '<p>{}</p>'.format(status)
				total_weight += weight
		score = (score * 100) // total_weight
		return (score, details_string)

	def runTestCase(self, code, data_input, data_output, verbose = True, show_output_details = False):
		code = code.replace('___INJECTION_LOCATION___', str(data_input))
		open(CODE_PATH, 'w').write(code)

		correct = False
		status = 'Internal Error'

		raw_output = ['(no output)']

		try:
			the_output = runcode.execute(timeout = self.run_timeout)
			raw_output = [i.strip() for i in the_output]
			if not self.case_sensitive:
				the_output = [i.lower() for i in the_output]
				data_output = [i.lower() for i in data_output]
			if verbose:
				print('    E:', data_output)
				print('    O:', the_output)
			if len(data_output) == len(the_output):
				correct = True
				for i in range(len(data_output)):
					if data_output[i].strip() != the_output[i].strip():
						correct = False
			if correct:
				status = 'Correct'
			else:
				status = 'Incorrect'
			
		except runcode.Timeout:
			status = 'Timeout'
		except runcode.Crashed as e:
			status = 'Crashed'
			raw_output = str(e).split('\n')

		# if verbose:

		if not show_output_details:
			raw_output = None

		return (correct, status, raw_output)

		