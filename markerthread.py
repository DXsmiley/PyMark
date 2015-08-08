import threading
import time
import marksingle
import submissions

class MarkerThread:

	def __init__(self, interval = 1):
		self.interval = interval
		thread = threading.Thread(target = self.run, args = ())
		thread.daemon = True
		thread.start()

	def run(self):
		while True:

			work_to_do = False

			marker_queue_lock.acquire()
			if len(marker_queue) > 0:
				problem, submisson_id, username = marker_queue.pop(0)
				work_to_do = True
			marker_queue_lock.release()
			
			if work_to_do:
				# save_path = './submissions/{}.py'.format(submisson_id)
				# score_path = './scores/{}'.format(submisson_id)
				print('Marking', problem, submisson_id, username)
				score = -2
				html = '...'
				try:
					the_code = submissions.get_code(submisson_id)
					score, html = marksingle.mark(problem, the_code)
				except Exception as e:
					score = -3
					submissions.store_result(username, problem, submisson_id, 0, html, error = 'Internal Error (-3)')
					print('Serious internal error while marking (-3):', e)
				if score == -1:
					submissions.store_result(username, problem, submisson_id, 0, html, error = 'Internal Error (-1)')
					print('The marker crashed (-1)')
				elif score == -2:
					submissions.store_result(username, problem, submisson_id, 0, html, error = 'Internal Error (-2)')
					print('Internal error while marking (-2)')
				elif score != -3:
					submissions.store_result(username, problem, submisson_id, score, html)
					print('Finished marking')

			time.sleep(self.interval)

def queue_item(item):
	marker_queue_lock.acquire()
	marker_queue.append(item)
	marker_queue_lock.release()

# submission_log_lock = threading.Lock()
marker_queue_lock = threading.Lock()
marker_queue = []
marker_thread = MarkerThread(interval = 4)