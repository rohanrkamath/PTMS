from typing import List
from fastapi import HTTPException
from pymongo.collection import Collection
from bson import ObjectId
from utils.task_management.checkIdExists import check_id_exists

def validate_members_for_entity(entity_id: str, proposed_members: List[str], current_user_email: str, entity_collection: Collection, entity_name: str = "entity"):
    entity = check_id_exists(entity_id, entity_collection, entity_name)
    entity_members = set(entity['members'])
    
    if current_user_email not in entity_members:
        raise HTTPException(status_code=403, detail=f"Current user not part of the {entity_name}")
    
    non_entity_members = [member for member in proposed_members if member not in entity_members]
    if non_entity_members:
        raise HTTPException(status_code=400, detail=f"Users not in {entity_name}: {', '.join(non_entity_members)}")