from fastapi import HTTPException
from pymongo.collection import Collection
from bson import ObjectId

def check_entity_belongs_to_parent(child_id: str, parent_id: str, child_collection: Collection, parent_field: str, child_name: str, parent_name: str):
    try:
        obj_child_id = ObjectId(child_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format for the {child_name} ID: {str(e)}")

    # Fetch the child entity and check if its parent_field matches the parent_id
    child_entity = child_collection.find_one({"_id": obj_child_id})
    if not child_entity:
        raise HTTPException(status_code=404, detail=f"{child_name} entity not found")

    # Check if the child entity's parent field matches the provided parent ID
    if child_entity.get(parent_field) != parent_id:
        raise HTTPException(status_code=404, detail=f"The specified {child_name} ID does not belong to the given {parent_name} ID.")
