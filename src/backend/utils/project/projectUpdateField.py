from fastapi import HTTPException
from bson.objectid import ObjectId
from database import db, archive

from datetime import datetime

from schema.project import ProjectInDB

projects_collection = db.projects

async def update_project_field(project_id: str, field_name: str, new_value, current_user: dict):
    project_id_obj = ObjectId(project_id)
    existing_project = projects_collection.find_one({"_id": project_id_obj})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = {
        field_name: new_value,
        "updated_at": datetime.utcnow(),  # Set the updated_at to the current UTC time
        "updated_by": current_user["email"]  # Use the email from the current_user dict
    }

    result = projects_collection.update_one(
        {"_id": project_id_obj},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        return {"message": "No changes made to the project"}

    updated_project = projects_collection.find_one({"_id": project_id_obj})
    updated_project["id"] = str(updated_project.pop("_id"))
    return ProjectInDB(**updated_project)