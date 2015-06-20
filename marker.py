from os import listdir
from os.path import isfile, join
import sys
import json
import importlib

program_to_mark = None
VERBOSE = False;

for i in sys.argv[1:]:
	if i[0] != '-':
		program_to_mark = i
	else:
		if i == '-verbose' or i == '-v':
			VERBOSE = True
		else:
			print('unknown flag:', i)

if program_to_mark == None:

	print('Usage: python marker.py ProblemName [-verbose]')

else:

	print('Marking Problem: ', program_to_mark)

	THE_FOLDER = "./problems/" + program_to_mark + "/"

	grader = None

	with open(THE_FOLDER + 'settings.json') as file_opts:
		jdata = json.loads(file_opts.read())
		grader_name = jdata['grader']
		command = importlib.import_module(grader_name)
		grader = command.Grader()
		# At some point, I might make the 'grader settings' argument mandatory.
		if 'grader settings' in jdata:
			grader.preload(THE_FOLDER, settings = jdata['grader settings'])
		else:
			grader.preload(THE_FOLDER)

	assert(grader != None)

	# Get all files in a specific directory
	def getFiles(path, ext = None):
		files = [ join(path, i) for i in listdir(path)]
		files = [ i for i in files if isfile(i) ]
		if ext != None:
			files = [ i for i in files if i.endswith("." + ext) ]
		return files

	all_scores = []

	# Mark all .py files
	for i in getFiles(THE_FOLDER + "User/", 'py'):
		name = i.split('/')[-1].split('_')[0].strip()
		print("Marking Code:", name, i)
		the_score = grader.evaluate(open(i).read(), verbose = VERBOSE)
		all_scores.append((the_score, name))

	# Sort results by score
	all_scores.sort(key = lambda x: x[0], reverse = True)

	# Print results
	print('Scores')
	for i in all_scores:
		print('    {:>3} - {}'.format(*i))

	grader.cleanup(THE_FOLDER)

