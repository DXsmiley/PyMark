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
		global current

		while True:

			work_to_do = False

			marker_queue_lock.acquire()
			if len(marker_queue) > 0:
				current = marker_queue.pop(0)
				problem, submisson_id, username = current
				work_to_do = True
			marker_queue_lock.release()
			
			if work_to_do:
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

				marker_queue_lock.acquire()
				current = ('Nothing', 'Nothing', 'Nothing')
				marker_queue_lock.release()

			time.sleep(self.interval)

def format_item(item):
	problem, submisson_id, username = item
	return '{} : {}'.format(username, problem)

def queue_item(item):
	marker_queue_lock.acquire()
	marker_queue.append(item)
	marker_queue_lock.release()

def queue_details():
	marker_queue_lock.acquire()
	result = [format_item(current)]
	for i in marker_queue:
		result.append(format_item(i))
	marker_queue_lock.release()
	return result

current = ('Nothing', 'Nothing', 'Nothing')
marker_queue_lock = threading.Lock()
marker_queue = []
marker_thread = MarkerThread(interval = 4)