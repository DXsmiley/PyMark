from os import listdir
from os.path import isfile, join
import sys
import json
import importlib
import traceback
import cgi
import submissions
import problems

def mark(problem_to_mark, code):

	# Mark things

	final_result = -2

	try:

		print('Marking Problem: ', problem_to_mark)

		# THE_FOLDER = "./problems/" + problem_to_mark + "/"
		VERBOSE = False

		grader = None

		problem_data = problems.get(problem_to_mark)
		grader_name = problem_data['grader']
		command = importlib.import_module(grader_name)
		grader = command.Grader()
		grader.preload(problem_data)

		grader_output = grader.evaluate(code, verbose = VERBOSE)
		final_result = int(grader_output[0])

		html_results = """<h1>Submission for {}</h1>
			<h2>Final Score: {}</h2>
			{}""".format(problem_to_mark, grader_output[0], grader_output[1])

	except Exception as e:

		error_text = traceback.format_exc()
		print(error_text)
		final_result = -1

		html_results = """<h1>Submission for {}</h1>
			<p>A <i>serious interal error</i> occured.
			You should try resubmitting your code.
			If the problem persists, conact the system administrators.</p>
			<pre>{}</pre>
			""".format(cgi.escape(error_text.replace('\n', '<br>')))
	
	try:
		grader.cleanup()
	except:
		pass

	return final_result, html_results
