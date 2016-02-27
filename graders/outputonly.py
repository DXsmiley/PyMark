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

# It supports the following grader options:
# "case sentitive" : boolean : output is considerd even if the case doesn't match
# "batched"        : boolean : requires that all cases for a subtask are passed to get the points
# "timeout"        : integer : timeout for each test case
# "short circuit"  : boolean : if the code fails a single case in a batch, subsequent cases are not run; activates batched mode

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

# This is the path that should be used to run code
CODE_PATH = './rundir/code.py'

def score_colour(score):
	if score == 100:
		return 'success'
	if score == 0:
		return 'danger'
	if score == -1:
		return 'active'
	return 'warning'

class Grader(BaseGrader):

	def __init__(self):
		self.test_cases = []
		self.case_sensitive = True
		self.run_timeout = 3
		self.batched = False
		self.code = ''
		self.short_circuit = False

	def preload(self, problem_data, settings = None):
		self.test_cases = problem_data['cases']
		if type(self.test_cases) is str:
			self.test_cases = json.loads(self.test_cases)
		# If we're using the old format, we need to convert it.
		if type(self.test_cases) is dict:
			new_cases = []
			for name, cases in self.test_cases.items():
				new_cases.append({
					'name': name,
					'cases': cases
					})
			self.test_cases = new_cases
		if settings != None:
			self.case_sensitive = settings.get('case sensitive', True)
			self.run_timeout = settings.get('timeout', 3)
			self.short_circuit = settings.get('short circuit', False)
			self.batched = settings.get('batched', self.short_circuit)

	def cleanup(self):
		os.remove(CODE_PATH)

	def score_subtask(self, subtask, scores, verbose = False):
		if self.batched:
			return min(scores)
		else:
			return sum(scores) // len(scores)

	def score_case(self, case, subtask, program_output, verbose = False):
		e_output = case.get('Output') or case.get('output')
		if len(program_output) != len(e_output):
			return 0
		for i, j in zip(program_output, e_output):
			if not self.case_sensitive:
				i = i.lower()
				j = j.lower()
			if i.strip() != j.strip():
				return 0
		return 100

	def run_test_case(self, case, subtask, verbose = False):
		e_input = case.get('Input') or case.get('input')
		code = self.code.replace('___INJECTION_LOCATION___', str(e_input))
		open(CODE_PATH, 'w').write(code)
		score = 0
		the_output = ['(no output)']
		status = 'No Status : Internal Error'
		try:
			the_output = runcode.execute(timeout = self.run_timeout)
			score = self.score_case(case, subtask, the_output)
			if score == 0:
				status = 'Incorrect'
			elif score == 100:
				status = 'Correct'
			else:
				status = 'Partially Correct'
		except runcode.Timeout:
			status = 'Timeout'
		except runcode.Crashed:
			status = 'Crashed'
		return (score, status, the_output)

	def evaluate(self, code, verbose = False):
		self.code = sandbox_code + code
		final_score = 0
		total_weight = 0
		full_results = []

		for sub_data in self.test_cases:
			sub_results = []
			has_failed = False
			for case in sub_data['cases']:
				if has_failed and self.short_circuit:
					sub_results.append((-1, 'Not Run'))
				else:
					score, status, the_output = self.run_test_case(case, sub_data['name'])
					sub_results.append((score, status))
					if score == 0:
						has_failed = True
			sub_score = self.score_subtask(case, [max(0, i[0]) for i in sub_results])
			sub_weight = sub_data.get('weight', 100)
			total_weight += sub_weight
			sub_score = (sub_score * sub_weight) // 100
			final_score += sub_score
			full_results.append((sub_data['name'], sub_score, sub_weight, sub_results))

		final_score = (final_score * 100) // total_weight
		html_result = '<h2 class="{}">Final Score: {}</h2>'.format(score_colour(final_score), final_score)
		
		for sub_name, sub_score, sub_weight, sub_results in full_results:

			html_result += """
				<h3>{} : {} / {}</h3>
				<table class="table table-condensed">
					<thead>
						<th>Case</th>
						<th>Status</th>
						<th>Score</th>
					</thead>
					<tbody>
				""".format(sub_name, sub_weight, sub_score)
			for i, (score, status) in enumerate(sub_results):
				colour = score_colour(score)
				html_result += """
					<tr class="{}">
						<td><p>{}</p></td>
						<td><p>{}</p></td>
						<td><p>{}</p></td>
					</tr>
					""".format(colour, i + 1, status, max(0, score))
			html_result += """
					</tbody>
				</table>
				"""

		return (final_score, html_result)
