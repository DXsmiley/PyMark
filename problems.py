import databases
import collections

class ErrorProblemAlreadyExists(Exception): pass
class ErrorProblemDoesntExist(Exception): pass

def get(short_name, q_filter = None):
	doc = databases.c_problems.find_one({'_id': short_name}, q_filter)
	if not doc:
		raise ErrorProblemDoesntExist(short_name)
	return doc

def get_meta(short_name):
	return get(short_name, {'cases': False})

def get_long_name(short_name):
	return get(short_name, {'long_name': True}).get('long_name')
	
def listing(show_disabled = False):
	listing = collections.defaultdict(list)
	the_filter = {'disabled': False} if not show_disabled else {}
	for i in databases.c_problems.find(the_filter, {'_id': True, 'group': True}):
		group = i.get('group', 'Uncategorised')
		listing[group].append(i['_id'])
	return listing

def list_names(show_disabled = False):
	listing = []
	the_filter = {'disabled': False} if not show_disabled else {}
	for i in databases.c_problems.find(the_filter, {'_id': True}):
		listing.append(i['_id'])
	return listing

def create(short_name, long_name, statement, cases, disabled = False, grader = 'graders.outputonly', group = 'Uncategorised'):
	doc = databases.c_problems.find_one({'_id': short_name})
	if doc != None:
		raise ErrorProblemAlreadyExists(short_name)
	problem_doc = {
		'_id': short_name,
		'long_name': long_name,
		'statement': statement,
		'disabled': disabled,
		'grader': grader,
		'cases': cases,
		'group': group
	}
	databases.c_problems.insert(problem_doc)

def edit(short_name, long_name, statement, cases, disabled = False, grader = 'graders.outputonly', group = 'Uncategorised'):
	doc = databases.c_problems.find_one({'_id': short_name})
	if doc == None:
		raise ErrorProblemDoesntExist(short_name)
	problem_doc = {
		'_id': short_name,
		'long_name': long_name,
		'statement': statement,
		'disabled': disabled,
		'grader': grader,
		'cases': cases,
		'group': group
	}
	databases.c_problems.replace_one({'_id': short_name}, problem_doc)