from fastapi import HTTPException
from pymongo.collection import Collection
from database import db

def check_id_exists(project_id: str, db: Collection):

    project = db.find_one({"_id": project_id})
    if project is None:
        raise HTTPException(status_code=404, detail="Project does not exist")
    
