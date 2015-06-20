from os import listdir
from os.path import isfile, join
import sys
import json
import importlib
import traceback
import cgi

def mark(problem_to_mark, code_filename, output_filename):

	# Mark things

	final_result = -2

	try:

		print('Marking Problem: ', problem_to_mark)

		THE_FOLDER = "./problems/" + problem_to_mark + "/"
		VERBOSE = False

		grader = None

		with open(THE_FOLDER + 'settings.json') as file_opts:
			jdata = json.loads(file_opts.read())
			grader_name = jdata['grader']
			command = importlib.import_module(grader_name)
			grader = command.Grader()
			if VERBOSE:
				print(grader_name, grader)
			# At some point, I might make the 'grader settings' argument mandatory.
			if 'grader settings' in jdata:
				grader.preload(THE_FOLDER, settings = jdata['grader settings'])
			else:
				grader.preload(THE_FOLDER)

		grader_output = grader.evaluate(open(code_filename).read(), verbose = VERBOSE)
		final_result = int(grader_output[0])

		with open(output_filename, 'w') as f:
			f.write('<h1>Submission for {}</h1>'.format(problem_to_mark))
			f.write('Your final score: {}<br>'.format(grader_output[0]))
			f.write(grader_output[1])

	except Exception as e:

		error_text = traceback.format_exc()
		print(error_text)
		final_result = -1
		with open(output_filename, 'w') as f:
			f.write('<h1>Submission for {}</h1>'.format(problem_to_mark))
			f.write("""
				<p>A <i>serious internal error</i> occured.
				You should try resubmitting your code.
				If the problem persists, conact the system administrators.</p>
				<p>{}</p>""".format(cgi.escape(error_text.replace('\n', '<br>'))))

	# Cleanup

	try:
		grader.cleanup(THE_FOLDER)
	except:
		pass

	return final_result
