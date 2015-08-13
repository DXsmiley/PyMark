import databases
import random
import zlib
import base64
import json

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

def get_local_problems():
	s = set()
	try:
		with open('./problems/problems.json') as f:
			jdata = json.loads(f.read())
			for i in jdata:
				for j in i['problems']:
					s.add(j)
	except FileNotFoundError:
		pass
	return s

def user_get_scores(username, problem = None):
	if problem == None:
		return list(databases.c_submissions.find({'username': username}))
	return list(databases.c_submissions.find({'username': username, 'problem': problem}))

def user_get_best_score(username, problem):
	best = 0
	for i in user_get_scores(username, problem):
		best = max(i['score'], best)
	return best

def user_get_num_solves(username, local_only = True):
	solved = set()
	problems = get_local_problems() if local_only else None
	for i in user_get_scores(username):
		if i['score'] == 100:
			if not local_only or i['problem'] in problems:
				solved.add(i['problem'])
	return len(solved)

def user_get_total_score(username, local_only = True):
	solved = {}
	problems = get_local_problems() if local_only else None
	for i in user_get_scores(username):
		p = i['problem']
		if not local_only or p in problems:
			solved[p] = max(solved.get(p, 0), i['score'])
	return sum(solved.values())