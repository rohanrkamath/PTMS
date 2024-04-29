from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError


MONGO_URI = 'mongodb://rohanrkamath:1234@localhost:27017/'
client = MongoClient(MONGO_URI)

db = client['task_management']
archive = client['archive']

db.users.create_index([("email", ASCENDING)], unique=True)
db.temp_users.create_index("created_at", expireAfterSeconds=300)

# roles = db.roles

# roles_data = [
#     {
#         "role_name": "admin",
#         "accessible_routers": ["auth_router", "user_router", "admin_router", "project_prime_router", 
#                                "project_router", "epic_router", "epic_prime_router", "task_router", 
#                                "subtask_router", "sprint_router", "timesheet_prime_router", "timesheet_router"]
#     },
#     {
#         "role_name": "project_manager",
#         "accessible_routers": ["auth_router", "user_router", "project_router", "epic_router", 
#                                "epic_prime_router", "task_router", "subtask_router", "sprint_router", 
#                                "timesheet_router"]
#     },
#     {
#         "role_name": "hr",
#         "accessible_routers": ["auth_router", "user_router", "timesheet_router"]
#     },
#     {
#         "role_name": "employee",
#         "accessible_routers": ["auth_router", "user_router", "project_router", "epic_router", 
#                                "task_router", "subtask_router", "timesheet_router"]
#     }
# ]

# # Inserting roles into the database
# try:
#     result = db.roles.insert_many(roles_data)
#     print(f"Inserted role IDs: {result.inserted_ids}")
# except PyMongoError as e:
#     print(f"Failed to insert roles: {str(e)}")

