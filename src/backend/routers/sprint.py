# from fastapi import APIRouter, HTTPException, Depends, Path, Query
# from sqlalchemy.orm import Session
# from datetime import datetime
# from typing import List

# from database import db, get_db
# from schema.sprint import SprintCreate, SprintUpdate, SprintInDB
# from utils.jwt_validation import get_current_user
# from utils.idCollectionCheck import check_id_exists
# # from utils.memberCheck import validate_project_members

# from uuid import uuid4

# sprint = APIRouter(
#     prefix="/sprint",
#     tags=["sprints"],
#     dependencies=[Depends(get_current_user)]
# )

# project_collection = db.projects
# sprints_collection = db.sprints 

# # create a sprint
# @sprint.post("/", response_model=SprintInDB)
# async def create_sprint(sprint: SprintCreate, created_by: str = Depends(get_current_user)):

#     check_id_exists(sprint.project_id, project_collection)

#     sprint_data = sprint.dict()
#     sprint_data["_id"] = uuid4().hex
#     sprint_data["sprint_created"] = datetime.now()
#     sprint_data["updated_at"] = None
#     sprint_data["created_by"] = created_by

#     try:
#         result = sprints_collection.insert_one(sprint_data)
#         if result.inserted_id:
#             sprint_data["id"] = sprint_data.pop("_id")
#             return SprintInDB(**sprint_data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create Sprint: {str(e)}")

#     raise HTTPException(status_code=500, detail="Sprint could not be created")

# # read sprint
# @sprint.get("/{sprint_id}", response_model=SprintInDB)
# async def read_sprint(sprint_id: str = Path(...)):
#     sprint_data = sprints_collection.find_one({"_id": sprint_id})
#     if sprint_data:
#         sprint_data["id"] = sprint_data.pop("_id")
#         return SprintInDB(**sprint_data)
#     raise HTTPException(status_code=404, detail="Sprint not found")

# # get sprints associated to a project
# # route is throwing an error, needs to be fixed
# @sprint.get("/project_id/{project_id}", response_model=List[SprintInDB])
# async def read_sprints_by_project(project_id: str = Path(...)):
#     sprints_data = list(sprints_collection.find({"project_id": project_id}))

#     if not sprints_data:
#         raise HTTPException(status_code=404, detail="No sprints found for the specified project")

#     # convert from MongoDB document to Pydantic model
#     for sprint in sprints_data:
#         sprint["id"] = sprint.pop("_id")
#     return [SprintInDB(**sprint) for sprint in sprints_data]

# # update a sprint
# @sprint.put("/{sprint_id}", response_model=SprintInDB)
# async def update_sprint(sprint_id: str = Path(...), sprint: SprintUpdate = Depends()):
#     existing_sprint = sprints_collection.find_one({"_id": sprint_id})
#     if not existing_sprint:
#         raise HTTPException(status_code=404, detail="Sprint not found")

#     update_data = sprint.dict(exclude_unset=True)
#     update_data["updated_at"] = datetime.now()

#     try:
#         result = sprints_collection.update_one({"_id": sprint_id}, {"$set": update_data})
#         if result.modified_count == 1:
#             updated_sprint = {**existing_sprint, **update_data}
#             updated_sprint["id"] = updated_sprint.pop("_id")
#             return SprintInDB(**updated_sprint)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update Sprint: {str(e)}")

#     raise HTTPException(status_code=500, detail="Sprint could not be updated")

# # delete a sprint
# @sprint.delete("/{sprint_id}", response_model=SprintInDB)
# async def delete_sprint(sprint_id: str = Path(...)):
#     existing_sprint = sprints_collection.find_one({"_id": sprint_id})
#     if not existing_sprint:
#         raise HTTPException(status_code=404, detail="Sprint not found")

#     try:
#         result = sprints_collection.delete_one({"_id": sprint_id})
#         if result.deleted_count == 1:
#             existing_sprint["id"] = existing_sprint.pop("_id")
#             return SprintInDB(**existing_sprint)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to delete Sprint: {str(e)}")

#     raise HTTPException(status_code=500, detail="Sprint could not be deleted")
