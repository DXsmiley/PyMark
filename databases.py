import pymongo
import settings

db_connection = pymongo.MongoClient(settings.get('db_login'))
database = db_connection[settings.get('db_name')]
c_accounts = database['accounts']
c_sessions = database['sessions']
c_submissions = database['submissions']
c_code = database['code']