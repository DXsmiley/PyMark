import pymongo
import settings

db_login = settings.get('db_login')
db_name = settings.get('db_name')

if db_login == None:
	db_connection = pymongo.MongoClient()
else:
	db_connection = pymongo.MongoClient(settings.get('db_login'))

database = db_connection[db_name]
c_accounts = database['accounts']
c_sessions = database['sessions']
c_submissions = database['submissions']
c_code = database['code']
c_problems = database['problems']