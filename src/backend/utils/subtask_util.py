from fastapi import HTTPException
from bson import ObjectId
from typing import List
from pymongo.collection import Collection
from datetime import datetime

from database import db

tasks_collection = db.tasks
subtasks_collection = db.subtasks  # Assuming you have a collection for subtasks

import logging

# def is_user_member_of_task(user_email: str, task_id: str, tasks_collection: Collection):
#     try:
#         obj_task_id = ObjectId(task_id)  # Ensure the task_id is a valid ObjectId
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Invalid task ID format: {str(e)}")

#     try:
#         task = tasks_collection.find_one({"_id": obj_task_id}, {"members": 1})
#         logging.debug(f"Task retrieved for ID {task_id}: {task}")

#         if task and user_email in task.get('members', []):
#             logging.debug(f"User {user_email} is a member of the task.")
#             return True
#         else:
#             logging.debug(f"User {user_email} is not a member of the task.")
#             return False
#     except Exception as e:
#         logging.error(f"Error checking membership for user {user_email} in task {task_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error checking membership: {str(e)}")


# def is_user_member_of_task(user_email: str, task_id: str, tasks_collection: Collection):
#     try:
#         task = tasks_collection.find_one({"_id": ObjectId(task_id)}, {"members": 1})
#         print(user_email)
#         print(task.get('members', []))
#         if task and user_email in task.get('members', []):
#             return True
#         return False
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error checking membership: {str(e)}")

def is_user_member_of_task(user_email: str, task_id: str, tasks_collection: Collection):
    try:
        # Ensure the task_id is a valid ObjectId
        task_obj_id = ObjectId(task_id)
        task = tasks_collection.find_one({"_id": task_obj_id}, {"members": 1})
        print(user_email, task["members"])
        if not task:
            logging.warning(f"No task found with ID: {task_id}")
            raise HTTPException(status_code=404, detail="Task not found")
        
        # print(user_email, task.get('members', []))

        # Check if the user's email is in the task's members list
        if user_email in task.get('members', []):
            logging.info(f"User {user_email} is a member of task {task_id}")
            return True
        
        logging.warning(f"User {user_email} is not a member of task {task_id}")
        return False
    
    except Exception as e:
        logging.error(f"Error checking membership for user {user_email} in task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking membership: {str(e)}")

def validate_subtask_members(subtask_id: str, proposed_members: List[str], tasks_collection: Collection, subtasks_collection: Collection):
    subtask = subtasks_collection.find_one({"_id": ObjectId(subtask_id)}, {"task_id": 1})
    if not subtask or 'task_id' not in subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    task = tasks_collection.find_one({"_id": ObjectId(subtask['task_id'])}, {"members": 1})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found for the subtask")

    task_members = set(task.get('members', []))

    non_task_members = [member for member in proposed_members if member not in task_members]

    print("non task members", non_task_members)
    if non_task_members:
        raise HTTPException(status_code=400, detail=f"The following users are not members of the task and cannot be added to the subtask: {', '.join(non_task_members)}")

    # return True  # Return True if validation passes without any exceptions
