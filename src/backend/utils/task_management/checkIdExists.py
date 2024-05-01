from typing import List
from fastapi import HTTPException
from pymongo.collection import Collection
from bson import ObjectId

def check_id_exists(entity_id: str, db: Collection, entity_name: str = "entity"):
    entity = db.find_one({"_id": ObjectId(entity_id)})
    if not entity:
        raise HTTPException(status_code=404, detail=f"{entity_name.capitalize()} not found")
    return entity