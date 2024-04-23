from fastapi import FastAPI, APIRouter, HTTPException, Body, Path
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId

from schema.project import ProjectBase, ProjectCreate, ProjectUpdate
from utils.crud import create_project, read_project, update_project, delete_project

from database import db

project = APIRouter()

projects_collection = db['projects']

def parse_json(data):
    return {k: str(v) if isinstance(v, ObjectId) else v for k, v in data.items()}

@project.post("/projects/", response_model=ProjectBase)
def create_project_endpoint(project: ProjectCreate = Body(...)):
    project_id = create_project(project.dict(by_alias=True))
    return read_project(project_id)

@project.get("/projects/{project_id}", response_model=ProjectBase)
def read_project_endpoint(project_id: str = Path(..., alias='id')):
    project = read_project(project_id)
    if project:
        return project
    raise HTTPException(status_code=404, detail="Project not found")

@project.put("/projects/{project_id}", response_model=ProjectBase)
def update_project_endpoint(project_id: str, project: ProjectUpdate = Body(...)):
    updated_project = update_project(project_id, project.dict(by_alias=True))
    if updated_project:
        return updated_project
    raise HTTPException(status_code=404, detail="Project not found")

@project.delete("/projects/{project_id}")
def delete_project_endpoint(project_id: str):
    deleted_count = delete_project(project_id)
    if deleted_count:
        return {"message": "Project deleted successfully."}
    raise HTTPException(status_code=404, detail="Project not found")