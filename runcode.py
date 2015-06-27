import subprocess
import os

class Timeout(Exception):
	pass

class Crashed(Exception):
	def __init__(self, data = ''):
		self.data = data
	def __str__(self):
		return 'Crash Report:\n' + self.data

def execute(command = None, timeout = 1):
	if command == None:
		command = os.environ.get("CMD_INVOKE_CODE", "python {}").format("code.py")
	try:
		the_output = subprocess.check_output(command, timeout = timeout, stderr = subprocess.STDOUT, cwd = './rundir')
		the_output = the_output.decode('utf-8').strip()
		the_output = [i.strip() for i in the_output.split('\n')]
		return the_output
	except subprocess.TimeoutExpired:
		raise Timeout()
	except subprocess.CalledProcessError as e:
		raise Crashed(e.output.decode('utf-8'))