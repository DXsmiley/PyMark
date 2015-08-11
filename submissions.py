import databases
import random
import zlib
import base64

def compress(s):
	return base64.b64encode(zlib.compress(bytes(str(str(s)), encoding = 'utf-8'), 9))

def decompress(b):
	return zlib.decompress(base64.b64decode(b)).decode('utf-8')

def store_code(username, code):
	cid = str(random.randint(0, 2 ** 128))
	doc = {
		'_id': cid,
		'username': username,
		'code': compress(code)
	}
	databases.c_code.insert(doc)
	return cid

def get_code(cid):
	doc = databases.c_code.find_one({'_id': cid})
	return decompress(doc['code'])

def store_result(username, problem, submission_id, score, breakdown, error = ''):
	doc = {
		'_id': submission_id,
		'username': username,
		'problem': problem,
		'score': score,
		'breakdown': compress(breakdown),
		'error': error
	}
	databases.c_submissions.insert(doc)

def get_result(submission_id):
	doc = databases.c_submissions.find_one({'_id': submission_id})
	doc['breakdown'] = decompress(doc['breakdown'])
	return doc

def user_get_scores(username, problem = None):
	if problem == None:
		return list(databases.c_submissions.find({'username': username}))
	return list(databases.c_submissions.find({'username': username, 'problem': problem}))

def user_get_best_score(username, problem):
	best = 0
	for i in user_get_scores(username, problem):
		best = max(i['score'], best)
	return best

def user_get_num_solves(username):
	solved = set()
	for i in user_get_scores(username):
		if i['score'] == 100:
			solved.add(i['problem'])
	return len(solved)