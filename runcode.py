import subprocess
import settings

class Timeout(Exception):
	pass

class Crashed(Exception):
	def __init__(self, data = ''):
		self.data = data
	def __str__(self):
		return 'Crash Report:\n' + self.data

def execute(command = None, timeout = 1, shell = None):
	if command == None:
		command = settings.get('invoke_code').format("code.py")
	if shell == None:
		if int(settings.get('invoke_shell')) == 1:
			shell = True
		else:
			shell = False
	try:
		the_output = subprocess.check_output(command, timeout = timeout, stderr = subprocess.STDOUT, cwd = './rundir', shell = shell)
		the_output = the_output.decode('utf-8').strip()
		the_output = [i.strip() for i in the_output.split('\n')]
		return the_output
	except subprocess.TimeoutExpired:
		raise Timeout()
	except subprocess.CalledProcessError as e:
		raise Crashed(e.output.decode('utf-8'))