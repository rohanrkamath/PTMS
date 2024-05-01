from fastapi import HTTPException
from bson import ObjectId
from database import db
from schema.project import MembersUpdate, ProjectInDB
from datetime import datetime
from schema.epic import EpicInDB

epics_collection = db.epics

async def update_epic_members_field(epic_id: str, members_update: MembersUpdate, current_user: dict):
    epic_id_obj = ObjectId(epic_id)
    existing_epic = epics_collection.find_one({"_id": epic_id_obj})
    if not existing_epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    current_members = set(existing_epic.get('members', []))
    members_to_add = set(members_update.add_members)
    members_to_remove = set(members_update.remove_members)

    updated_members = (current_members - members_to_remove).union(members_to_add)

    update_data = {
        "members": list(updated_members),
        "updated_at": datetime.utcnow(),
        "updated_by": current_user["email"]
    }

    result = epics_collection.update_one({"_id": epic_id_obj}, {"$set": update_data})
    if result.modified_count == 0:
        return {"message": "No changes made to the epic"}

    updated_epic = epics_collection.find_one({"_id": epic_id_obj})
    updated_epic["id"] = str(updated_epic.pop("_id"))
    return EpicInDB(**updated_epic)
