import bottle
import json
import random
import marksingle
import threading
import markerthread
import time
import datetime
import accounts
import datetime
import cgi
import os

html_framework = """
	<html>
		<head>
			<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css" />
			<link rel="stylesheet" href="/static/callouts.css" />
			<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
			<script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
			<title>PyMark Code Judge</title>
		</head>
		<body>
			<nav class="navbar navbar-inverse navbar-static-top">
				<div class="container-fluid">
					<div class="navbar-header">
						<a class="navbar-brand" href="/">PyMark</a>
					</div>
					<div>
						<ul class="nav navbar-nav">
							<li><a href="/">Home</a></li>
							<li><a href="/problems">Problems</a></li> 
							<li><a href="/users">Users</a></li>
							<li><a href="/highscores">Highscores</a></li>
							<li><a href="/my_account">Account</a></li>
						</ul>
					</div>
				</div>
			</nav>
			<div class="container">
				{}
			</div>
		</body>
	</html>
	"""

### SETUP ##################################################################################

def ensure_directory_exists(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
		print('Creating directory', directory)

def ensure_file_exists(filename, contents = ''):
	try:
		with open(filename, 'x') as f:
			f.write(contents)
		print('Creating file', filename)
	except FileExistsError:
		pass

ensure_directory_exists('./problems')
ensure_directory_exists('./progress')
ensure_directory_exists('./rundir')
ensure_directory_exists('./scores')
ensure_directory_exists('./submissions')
ensure_directory_exists('./static')
ensure_directory_exists('./static/pages')

ensure_file_exists('./problems/problems.json', '{}')

accounts.load()

### GENERAL STUFF ##########################################################################

@bottle.route('/static/<the_file>')
def static(the_file):
	return bottle.static_file(the_file, root = './static/')

@bottle.route('/static/page/<the_file>')
def static(the_file):
	html = open('./static/page/' + the_file).read()
	return html_framework.format(html)

@bottle.route('/')
def index():
	s = """
		<h1>PyMark Code Judge</h1>
		<p><a href="/problems">Here is a list of problems.</a></p>
		<p>Welcome to the normanhurst code judge. It's still in development,
			so don't be surprised if things go wrong.</p>
		<p>Before you start solving problems, you'll have to
			<a href="/newaccount">create an account</a> and
			<a href="/login">login</a>.</p>
		<div class="bs-callout bs-callout-danger">
			<h4>Warning!</h4>
			<p>Please only submit to problems that have a problem statement <i>on this site</i>.
			Other problems will not work, or are unstable.</p>
		</div>
		<div class="bs-callout bs-callout-info">
			<h4>Help</h4>
			<p>If anyone needs any help, just ask. I'm also able to fix any problems that are broken.</p>
		</div>
		"""
	return html_framework.format(s)

@bottle.route('/favicon.ico')
def favicon():
	return bottle.static_file('./favicon.png', root = './static')

### ACCOUNT MANAGEMENT #####################################################################

def login_form(error = None):
	contents = """
		<h1>Login</h1>
		<form action="/login" method="post" enctype="multipart/form-data">
			<div class="form-group">
				<label>Username</label>
				<input type="text" class="form-control" name="username">
			</div>
			<div class="form-group">
				<label>Password</label>
				<input type="password" class="form-control" name="password">
			</div>
			<button type="submit" class="btn btn-default">Login</button>
		</form>
		<p>Don't have an account? <a href="/newaccount">Create one!</a></p>
		"""
	if error:
		contents = """
			<div class="bs-callout bs-callout-danger">
				<h4>Error</h4>
				<p>{}</p>
			</div>""".format(error) + contents
	return contents

@bottle.route('/login', method = 'GET')
def login_get():
	return html_framework.format(login_form())

@bottle.route('/login', method = 'POST')
def login_post():
	username = bottle.request.forms.get('username')
	password = bottle.request.forms.get('password')
	contents = ''
	try:
		session_id, session_key = accounts.login(username, password)
		contents = """
			<h1>Login Successful</h1>
			"""
		bottle.response.set_cookie('session_id', session_id)
		bottle.response.set_cookie('session_key', session_key)
		print('Login:', username)
	except accounts.ErrorInvalidLogin as e:
		contents = login_form(e.message())
	return html_framework.format(contents)

@bottle.route('/logout')
def logout():
	bottle.response.delete_cookie('session_id')
	bottle.response.delete_cookie('session_key')
	return html_framework.format('<h1>Loged out</h1>')

def newaccount_form(error = None):
	contents = """
		<h1>Create Account</h1>
		<form action="/newaccount" method="post" enctype="multipart/form-data">
			<div class="form-group">
				<label>Username</label>
				<input type="text" class="form-control" name="username">
			</div>
			<div class="form-group">
				<label>Password</label>
				<input type="password" class="form-control" name="password">
			</div>
			<div class="form-group">
				<label>Password Again</label>
				<input type="password" class="form-control" name="password2">
			</div>
			<button type="submit" class="btn btn-default">Create Account</button>
		</form>
		<p>Already have an account? <a href="/login">Login!</a></p>
		<ul>
			<li>Usernames must contain only letters and numbers.</li>
			<li>Usernames and passwords must be at least 4 characters long.</li>
			<li>Usernames must not be longer that 20 characters.</li>
		<ul>
		"""
	if error != None:
		contents = """
			<div class="bs-callout bs-callout-danger">
				<h4>Error</h4>
				<p>{}</p>
			</div>
			""".format(error) + contents
	return contents

@bottle.route('/newaccount', method = 'GET')
def newaccount_get():
	return html_framework.format(newaccount_form())

@bottle.route('/newaccount', method = 'POST')
def newaccount_post():
	username = bottle.request.forms.get('username')
	password = bottle.request.forms.get('password')
	password2 = bottle.request.forms.get('password2')
	contents = ''
	print('Trying to create account:', username)
	if password == password2:
		try:
			session_id, session_key = accounts.create(username, password)
			contents = """
				<h1>Account Created!</h1>
				"""
			bottle.response.set_cookie('session_id', session_id)
			bottle.response.set_cookie('session_key', session_key)
			print('Created account:', username)
		except accounts.ErrorBase as e:
			contents = newaccount_form(e.message())
	else:
		contents = newaccount_form('Passwords do not match.')
	return html_framework.format(contents)

@bottle.route('/accounts')
def account_list():
	contents = '<h1>Accounts</h1>'
	for i in accounts.list_accounts():
		contents += '<p>{}</p>'.format(i)
	return html_framework.format(contents)

def session_check():
	session_id = bottle.request.get_cookie('session_id')
	session_key = bottle.request.get_cookie('session_key')
	return accounts.session_check(session_id, session_key)

def session_get_account_data():
	assert(session_check())
	session_id = bottle.request.get_cookie('session_id')
	session_key = bottle.request.get_cookie('session_key')
	return accounts.session_get_account_data(session_id)

def session_get_username():
	assert(session_check())
	session_id = bottle.request.get_cookie('session_id')
	session_key = bottle.request.get_cookie('session_key')
	return accounts.session_get_username(session_id)

def session_get_auth_level():
	assert(session_check())
	session_id = bottle.request.get_cookie('session_id')
	session_key = bottle.request.get_cookie('session_key')
	return accounts.session_get_account_data(session_id).get('auth', 'student')

@bottle.route('/my_account')
def my_account():
	if session_check():
		contents = """
			<h1>My Account</h1>
			<p>You are loged in as {username}.</p>
			<p>You can view your public profile <a href="/user/{username}">here</a></p>
			<p><a href="/logout">Logout</a>.</p>
			""".format(username = session_get_username())
		return html_framework.format(contents)
	else:
		bottle.redirect('/login')

@bottle.route('/edit_account')
def edit_account():
	if session_check():
		contents = """
			<h1>My Account Settings</h1>
			<p>There's not much here</p>
			"""
		return html_framework.format(contents)
	else:
		bottle.redirect('/login')

### USERS ##################################################################################

@bottle.route('/user/<username>/change_auth_level', method = 'POST')
def user_change_auth_level(username):
	contents = '<p>You do not have permission to do that!</p>'
	if session_check():
		if session_get_auth_level() == 'admin':
			data = accounts.get_account_data(username)
			new_level = bottle.request.forms.get('auth_level')
			data['auth'] = new_level
			accounts.save()
			contents = '<p>{}\' level changed to {}.</p>'.format(username, new_level)
	return html_framework.format(contents)

@bottle.route('/user/<username>/change_visible', method = 'POST')
def user_change_visibility(username):
	contents = '<p>You do not have permission to do that!</p>'
	if session_check():
		if session_get_auth_level() == 'admin':
			data = accounts.get_account_data(username)
			new_visibility = bottle.request.forms.get('visible')
			data['visible'] = new_visibility == 'visible'
			accounts.save()
			contents = '<p>{}\' Visibility changed to {}.</p>'.format(username, new_visibility)
	return html_framework.format(contents)

@bottle.route('/user/<username>')
def user(username):
	data = accounts.get_account_data(username)
	if data == None:
		# html_framework.format('<p>User {} not found</p>'.format(username))
		raise bottle.HTTPError(status = 404)
	else:
		auth_level = {None: 'Student', 'tutor': 'Tutor', 'admin': 'Administrator', 'pleb': 'Pleb'}[data.get('auth')]
		contents = """
			<h1>User: {}</h1>
			<p>{}</p>
			<p>{}</p>
			""".format(username, auth_level, '' if data.get('visible', True) else 'Invisible')
		contents += """
			<!-- <h2>Problems Solved</h2> -->
			<button type="button" class="btn btn-info" data-toggle="collapse" data-target="#scores-collpse">Problems Solved</button>
			<div id="scores-collpse" class="collapse out">
				{}
			</div>
			<br>
			<br>
			""".format(problem_listing(username))
		contents += """
			<!-- <h2>Submissions</h2> -->
			<button type="button" class="btn btn-info" data-toggle="collapse" data-target="#submissions-collpse">Submissions</button>
			<div id="submissions-collpse" class="collapse out">
				{}
			</div>
			<br>
			<br>""".format(attempt_listing(username))
		if session_check() and session_get_auth_level() == 'admin':
			contents += """
				<h2>Change Authentication Level</h2>
				<form action="/user/{username}/change_auth_level" method="POST">
					<select name="auth_level">
						<option value="admin">Administrator</option>
						<option value="tutor">Tutor</option>
						<option selected="selected" value="student">Student</option>
						<option value="pleb">Pleb</option>
					</select><br>
					<button type="submit" class="btn btn-default">Apply</button>
				</form>
				<h2>Change Visibility</h2>
				<form action="/user/{username}/change_visible" method="POST">
					<select name="visible">
						<option value="visible" selected="selected">Visible</option>
						<option value="invisible">Invisiblae</option>
					</select><br>
					<button type="submit" class="btn btn-default">Apply</button>
				</form>
				""".format(username = username)
	return html_framework.format(contents)

@bottle.route('/users')
def user_list():
	contents = "<h1>Users</h1>"
	ac_list = accounts.list_accounts()
	ac_list.sort()
	for i in ac_list:
		contents += '<p><a href="/user/{0}">{0}</a></p>'.format(i)
	return html_framework.format(contents)

@bottle.route('/users/all')
def user_list_all():
	if session_check() and session_get_auth_level() in ['admin', 'tutor']:
		contents = """
			<h1>Users</h1>
			<p>Showing invisible users as well.</p>
			"""
		ac_list = accounts.list_accounts(show_invisible = True)
		ac_list.sort()
		for i in ac_list:
			contents += '<p><a href="/user/{0}">{0}</a></p>'.format(i)
	else:
		contents = """
			<div class="bs-callout bs-callout-danger">
				<h4>Access denied</h4>
				<p>You do not have the rights to access this page.</p>
			</div>
			"""
	return html_framework.format(contents)

### PROBLEM INFORMATION ####################################################################

def problem_get_long_name(i):
	fsettings = open('./problems/{}/settings.json'.format(i))
	return json.loads(fsettings.read()).get('name', i + ' (missing property: name)')

def problem_get_data(i):
	f = open('./problems/{}/settings.json'.format(i))
	return json.loads(f.read())

def user_get_scores(username):
	scores = dict()
	try:
		with open('./progress/' + username) as f:
			for line in f.readlines():
				problem, submisson_id, score = line.split()
				scores[problem] = max(scores.get(problem, 0), int(score))
	except FileNotFoundError:
		pass
	return scores

def user_get_best_submissions(username):
	scores = user_get_scores(username)
	submission = dict()
	try:
		with open('./progress/' + username) as f:
			for line in f.readlines():
				problem, submisson_id, score = line.split()
				if int(score) == scores[problem]:
					submission[problem] = submisson_id
	except FileNotFoundError:
		pass
	return submission

def user_get_num_solves(username):
	num_solves = 0
	for i, j in user_get_scores(username).items():
		if j == 100:
			num_solves += 1
	return num_solves

# Gives a listing of problems that the user has solved.
# This can be used for seeing other people's things and your own.
def problem_listing(username = None):
	scores = dict()
	submissions = dict()
	num_solves = 0

	if username != None:
		scores = user_get_scores(username)
		submissions = user_get_best_submissions(username)
		num_solves = user_get_num_solves(username)


	html = ''

	with open('./problems/problems.json') as f:
		jdata = json.loads(f.read())
		if len(jdata) == 0:
			html = """
				<p>There are no problems!</p>
				<p>The server admin can add some to the problem listing at <code>./problems/problems.json</code>.</p>
				"""
		else:
			html = """
				<table class="table">
					<thead>
						<th>Set</th>
						<th>Problem</th>
						<th>Score</th>
					</thead>
				"""
			for group_o in jdata:
				first = True
				html += ''.format()
				group_n = group_o['section']
				group_s = len(group_o['problems'])

				for problem in group_o['problems']:
					data = problem_get_data(problem)
					long_name = data.get('name', problem + ' (?)')
					required = data.get('required solves', 0)
					score = scores.get(problem, 'Not attempted')
					colour = ''
					if problem in scores:
						if scores[problem] == 100:
							colour = 'success'
						elif scores[problem] == 0:
							colour = 'danger'
						else:
							colour = 'warning'
					if num_solves < required:
						colour = 'active'
						score = '{} solves until unlock'.format(required - num_solves)
					if problem in submissions:
						score = '<a href="/scores/{}">{}</a>'.format(submissions[problem], score)
					if first:
						first = False
						html += """
							<tr>
								<td rowspan="{}">{}</td>
								<td class="{colour}"><a href="/statement/{}">{}</a></td>
								<td class="{colour}">{}</td>
							</tr>
							""".format(group_s, group_n, problem, long_name, score, colour = colour)
					else:
						html += """
							<tr>
								<td class="{colour}"><a href="/statement/{}">{}</a></td>
								<td class="{colour}">{}</td>
							</tr>
							""".format(problem, long_name, score, colour = colour)
			html += '</table>'

	return html

@bottle.route('/problems')
def problems():
	username = None
	if session_check():
		username = session_get_username()
	html = '<h1>Problems</h1>' + problem_listing(username)
	return html_framework.format(html)

def attempt_listing(username, problem = None):
	html = ''
	try:
		with open('./progress/' + username) as f:
			num_previous = 0
			for line in f.readlines():
				# print(line)
				s_problem, submisson_id, score = line.split()
				if problem == None:
					num_previous += 1
					html += '<p><a href="/scores/{}">{} {}: {}</a></p>'.format(submisson_id, submisson_id, s_problem, score)
				if s_problem == problem:
					num_previous += 1
					html += '<p><a href="/scores/{}">Submission {}: {}</a></p>'.format(submisson_id, num_previous, score)
	except FileNotFoundError:
		html = '<p>No progress file.</p>'
	return html

@bottle.route('/statement/<problem>')
def statement(problem):
	# Handle non-existant problems
	try:
		open('./problems/{}/settings.json'.format(problem))
	except FileNotFoundError:
		raise bottle.HTTPError(status = 404)
	# Get problem data
	problem_data = problem_get_data(problem)
	# Check if locked
	required_solves = problem_data.get('required solves', 0)
	has_access = True
	if required_solves > 0:
		if not session_check() or user_get_num_solves(session_get_username()) < required_solves:
			has_access = False
	# Warning about no problem statement
	statement = """
		<h1>{}</h1>
		<div class="bs-callout bs-callout-danger">
			<h4>Warning!</h4>
			<p>There is no problem statement for this question.
			It's probably unstable, so <i>don't submit code</i>.</p>
		</div>
		""".format(problem_data.get('name', problem))
	# Load problem statement
	try:
		with open('./problems/{}/statement.html'.format(problem)) as f:
			statement = f.read()
	except FileNotFoundError:
		pass
	# Create page
	if has_access or (session_check() and session_get_auth_level() in {'tutor', 'admin'}):
		if session_check():
			# Submit form
			foot = """
				<h2>Submit Code</h2>
				<form action="/dosubmit/{}" method="post" enctype="multipart/form-data">
					<div class="form-group">
						<!-- <label for="file_upload_thing">Upload File</label> -->
						<input type="file" id="file_upload_thing" name="upload">
						<!-- <p class="help-block">Example block-level help text here.</p> -->
					</div>
					<button type="submit" class="btn btn-default">Submit Code</button>
				</form>
			""".format(problem)
			# Previous attempts
			username = session_get_username()
			previous_attemtps = attempt_listing(username, problem)
			if previous_attemtps == '':
				previous_attemtps = '<p>You have not attempted this problem yet.</p>'
			foot += '<h1>Previous Attempts</h1>' + previous_attemtps
		else:
			foot = """
				<h2>Submit Code</h2>
				<div class="bs-callout bs-callout-info">
					<h4>Want your code judged?</h4>
					<p>You need to <a href="/newaccount">create an account</a> and then <a href="/login">login</a> before
					submitting code. It only takes a few seconds.</p>
				</div>
				"""
		head = ''
		if not has_access:
			head += """
				<div class="bs-callout">
					<h4>Exceptions were made</h4>
					<p>You do not have enough solves to view this problem under normal circumstances.</p>
				</div>
				"""
		return html_framework.format(head + statement + foot)
	else:
		contents = """
			<h1>{}</h1>
			<div class="bs-callout bs-callout-info">
				<h4>This problem is locked!</h4>
				<p>You have not solved a suficient number of other problems to unlock this one.</p>
				<p>Return to the <a href="/problems">problem list</a> to find problems that you can access.</p>
			</div>
			""".format(problem_data.get('name', problem))
		return html_framework.format(contents)

### SUBMISSIONS AND SCORES #################################################################

# Maybe, some year far into the future, the random number generator will mess up.
# Just makes sure that the file doesn't already exist.
def generateSubmissionId():
	valid = False
	while not valid:
		submisson_id = random.randint(0, 2 ** 30)
		try:
			open('./submissions/{}.py'.format(submisson_id))
		except FileNotFoundError:
			valid = True
	return submisson_id

def loadFileSafely(file_object, limit = 1024):
	BUFFER_SIZE = 1024 * 8
	byte_count = 0
	data = bytes()
	buff = file_object.read(BUFFER_SIZE)
	while buff and byte_count <= limit:
		byte_count += len(buff)
		data += buff
		buff = file_object.read(BUFFER_SIZE)
	if byte_count > limit:
		data = None
	return data

@bottle.route('/dosubmit/<problem>', method = 'POST')
def dosubmit(problem):
	if session_check():
		if problem_get_data(problem).get('disabled', False):
			contents = """
				<div class="bs-callout bs-callout-danger">
					<h4>Error!</h4>
					<p>This problem has been disabled! You may not submit to this problem.</p>
				</div>
				"""
		else:
			# Save code file
			o_upload = bottle.request.files.get('upload')
			submisson_id = generateSubmissionId()
			save_path = './submissions/{}.py'.format(submisson_id)
			score_path = './scores/{}'.format(submisson_id)

			# o_upload.save(save_path)

			# Load file, limit to 32 KB
			file_data = loadFileSafely(o_upload.file, 1024 * 32)

			if file_data != None:
				# File is within acceptable size, we can save and mark it.
				with open(save_path, 'wb') as f:
					f.write(file_data)
				markerthread.queue_item((problem, submisson_id, session_get_username()))
				# Save metatdata file
				with open('./submissions/{}.json'.format(submisson_id), 'w') as f:
					data = {
						'user': session_get_username(),
						'problem': problem,
						'date': str(datetime.datetime.now())
					}
					f.write(json.dumps(data))
				contents = """
					<p>
						File submitted for grading.<br>
						Your submission id is {}.<br>
						Your score will be avaliable soon <a href="/scores/{}">here</a>.
					</p>
					""".format(submisson_id, submisson_id)
			else:
				#File Exceeds size
				contents = """
					<div class="bs-callout bs-callout-danger">
						<h4>Error!</h4>
						<p>Your code file exceeded the maximum file size of 32 KB.
					</div>
					"""
		return html_framework.format(contents)
	else:
		bottle.redirect('/login')

def submission_get_data(submission):
	# Arbitrary dummy object that mimics a dictionary, and returns 'unknown' for everything.
	class temp:
		def get(self, *args):
			return '(unknown)'
	data = temp()
	# Now actually do stuff
	try:
		with open('./submissions/{}.json'.format(submission)) as f:
			data = json.loads(f.read())
	except:
		pass
	return data

def may_see_code(submission):
	assert(session_check())
	sub_data = submission_get_data(submission)
	ses_data = session_get_account_data()
	return ses_data.get('auth') in ['admin', 'tutor'] or session_get_username() == sub_data['user']

@bottle.route('/scores/<submission>')
def scores(submission):
	t = ''
	if session_check() and may_see_code(submission):
		t += '<p><a href="/code/{}">Code</a></p>'.format(submission)
	try:
		with open('./submissions/{}.json'.format(submission), 'r') as f:
			data = json.loads(f.read())
			t += '<a href="/statement/{}">Problem statement</a></p>'.format(data['problem'])
	except:
		pass
	e = '<p>Your code has not yet been judged. Try refreshing the page in a minute or two.</p>'
	s = html_framework.format(e)
	try:
		with open('./scores/' + submission) as f:
			s = html_framework.format(t + '<p>' + f.read() + '</p>')
	except:
		pass
	return s

@bottle.route('/code/<submission>')
def code(submission):
	if session_check() and may_see_code(submission):
		data = submission_get_data(submission)
		user = data.get('user')
		problem = data.get('problem')
		contents = """
			<p>{user}'s submission to <a href="/statement/{problem}">{problem}</a>.</p>
			""".format(user = user, problem = problem)
		the_code = open('./submissions/{}.py'.format(submission)).read()
		html_code = '<pre>{}</pre>'.format(cgi.escape(the_code))
		return html_framework.format(contents + html_code)
	else:
		return html_framework.format('<p>You do not have the right to access code.</p>')

@bottle.route('/log')
def log():
	s = 'Error'
	# submission_log_lock.acquire()
	with open('submission_log') as f:
		s = html_framework.format(f.read())
	# submission_log_lock.release()
	return s

@bottle.route('/highscores')
def highscores():
	contents = """
		<h1>Highscores</h1>
		<table class="table">
			<thead>
				<tr>
					<th>User</th>
					<th>Problems Solved</th>
				</tr>
			</thead>
			<tbody>
		"""
	scores = []
	for i in accounts.list_accounts():
		s = user_get_num_solves(i)
		if s > 0:
			scores.append((i, s))
	scores.sort(key = lambda x: x[1], reverse = True)
	for i, s, in scores:
		contents += """
			<tr>
				<td><a href="/user/{username}">{username}</td>
				<td>{score}</td>
			</tr>
			""".format(username = i, score = s)
	contents += """
			</tbody>
		</table>
		"""
	return html_framework.format(contents)

### ERROR HANDLING #########################################################################

@bottle.error(404)
def error404(error):
	contents = """
		<div class="bs-callout bs-callout-danger">
			<h4>Error: 404</h4>
			<p>The page you requested does not exist. If you think there's a problem with the site,
			talk to the system administrator.</p>
		</div>
		"""
	return html_framework.format(contents)

bottle.run(host = '0.0.0.0', port = 8080)