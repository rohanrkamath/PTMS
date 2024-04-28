from pymongo import MongoClient, ASCENDING


MONGO_URI = 'mongodb://rohanrkamath:1234@localhost:27017/'
client = MongoClient(MONGO_URI)
db = client['task_management']
archive = client['archive']

db.users.create_index([("email", ASCENDING)], unique=True)
db.temp_users.create_index("created_at", expireAfterSeconds=300)

