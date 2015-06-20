import threading
import time
import datetime
import marksingle

class MarkerThread:

	def __init__(self, interval = 1):
		self.interval = interval

		thread = threading.Thread(target = self.run, args = ())
		thread.daemon = True                            # Daemonize thread
		thread.start()                                  # Start the execution

	def save_result(self, problem, submisson_id, score, username, error = ''):

		dt_string = str(datetime.datetime.now())
		human_string = dt_string.split('.')[0]
		submission_log_lock.acquire()
		s = '<p>{} : {}\'s submission for {}: <a href="/scores/{}">{}</a>: {}</p>\n'
		with open('./submission_log', 'a') as f:
			f.write(s.format(human_string, username, problem, submisson_id, submisson_id, score))
		submission_log_lock.release()

		try:
			with open('./progress/{}'.format(username), 'a+') as f:
				f.write('{} {} {}\n'.format(problem, submisson_id, score))
			print('Saved progress')
		except FileNotFoundError:
			print('Progress file was not found')

	def run(self):
		while True:
			# Do something
			# print('Doing something imporant in the background')

			work_to_do = False

			marker_queue_lock.acquire()
			if len(marker_queue) > 0:
				problem, submisson_id, username = marker_queue.pop(0)
				work_to_do = True
			marker_queue_lock.release()
			
			if work_to_do:
				save_path = './submissions/{}.py'.format(submisson_id)
				score_path = './scores/{}'.format(submisson_id)
				print('Marking', problem, submisson_id, username)
				score = -2
				try:
					score = marksingle.mark(problem, save_path, score_path)
				except Exception as e:
					self.save_result(problem, submisson_id, 0, username, error = 'Internal Error (-3)')
					print('Serious internal error while marking (-3):', e)
				if score == -1:
					self.save_result(problem, submisson_id, 0, username, error = 'Internal Error (-1)')
					print('The marker crashed (-1)')
				elif score == -2:
					self.save_result(problem, submisson_id, 0, username, error = 'Internal Error (-2)')
					print('Internal error (-2)')
				else:
					self.save_result(problem, submisson_id, score, username)
					print('Finished marking')

			time.sleep(self.interval)

def queue_item(item):
	marker_queue_lock.acquire()
	marker_queue.append(item)
	marker_queue_lock.release()

submission_log_lock = threading.Lock()
marker_queue_lock = threading.Lock()
marker_queue = []
marker_thread = MarkerThread(interval = 4)