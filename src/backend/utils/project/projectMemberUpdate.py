from fastapi import HTTPException
from bson import ObjectId
from database import db
from schema.project import MembersUpdate, ProjectInDB
from datetime import datetime

projects_collection = db.projects

async def update_project_members_field(project_id: str, members_update: MembersUpdate, current_user: dict):
    project_id_obj = ObjectId(project_id)
    existing_project = projects_collection.find_one({"_id": project_id_obj})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Calculate the new set of members
    current_members = set(existing_project.get('members', []))
    members_to_add = set(members_update.add_members)
    members_to_remove = set(members_update.remove_members)

    # Update the set of members
    updated_members = (current_members - members_to_remove).union(members_to_add)

    update_data = {
        "members": list(updated_members),
        "updated_at": datetime.utcnow(),  
        "updated_by": current_user["email"]  
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