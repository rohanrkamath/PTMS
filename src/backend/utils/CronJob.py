# this file will be used to set up a cron job to clear temp table periodically

from database import db
from pymongo.errors import PyMongoError

temp_users_collection = db.temp_users

try:
    result = temp_users_collection.delete_many({}) 
    print(f"All temp users deleted successfully. Count: {result.deleted_count}")
except PyMongoError as e:
    print(f"Failed to delete temp users: {str(e)}")



