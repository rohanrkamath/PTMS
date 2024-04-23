from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date
import bson


# Helper function to handle ObjectId serialization
def to_camel(string: str) -> str:
    return ''.join(word.capitalize() if i else word for i, word in enumerate(string.split('_')))


class PyObjectId(bson.ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not bson.ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return str(bson.ObjectId(v))

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


# Project request schema

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    members: Optional[List[PyObjectId]] = []
    epics: Optional[List[PyObjectId]] = []

    class Config:
        allow_population_by_field_name = True
        json_encoders = {bson.ObjectId: str}
        alias_generator = to_camel
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "name": "New Project",
                "description": "This is a new project.",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "status": "In Progress",
                "members": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"],
                "epics": ["507f191e810c19729de860ea", "507f191e810c19729de860eb"]
            }
        }


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass

# Epic request schema

class EpicBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: PyObjectId
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    assignees: Optional[List[PyObjectId]] = []

class EpicCreate(EpicBase):
    pass

class EpicUpdate(EpicBase):
    pass

# Story request schema

class StoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    epic_id: PyObjectId
    subtasks: Optional[List[PyObjectId]] = []
    status: Optional[str] = None
    priority: Optional[str] = None
    assignees: Optional[List[PyObjectId]] = []
    sprint_id: Optional[PyObjectId] = None

class StoryCreate(StoryBase):
    pass

class StoryUpdate(StoryBase):
    pass

# Task request schema

class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    epic_id: PyObjectId
    subtasks: Optional[List[PyObjectId]] = []
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[PyObjectId] = None
    sprint_id: Optional[PyObjectId] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

# Bug request schema

class BugBase(BaseModel):
    name: str
    description: Optional[str] = None
    epic_id: PyObjectId
    subtasks: Optional[List[PyObjectId]] = []
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[PyObjectId] = None
    sprint_id: Optional[PyObjectId] = None

class BugCreate(BugBase):
    pass

class BugUpdate(BugBase):
    pass

# Subtask request schema

class SubtaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: PyObjectId
    time_to_be_spent: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[PyObjectId] = None

class SubtaskCreate(SubtaskBase):
    pass

class SubtaskUpdate(SubtaskBase):
    pass

# Sprint request schema

class SprintBase(BaseModel):
    name: str
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    associated_tasks: Optional[List[PyObjectId]] = []
    associated_stories: Optional[List[PyObjectId]] = []
    associated_bugs: Optional[List[PyObjectId]] = []

class SprintCreate(SprintBase):
    pass

class SprintUpdate(SprintBase):
    pass

# Timesheet request schema

class TimesheetBase(BaseModel):
    user_id: PyObjectId
    subtask_id: PyObjectId
    hours_worked: int
    date: date
    is_billable: bool
    status: Optional[str] = None

class TimesheetCreate(TimesheetBase):
    pass

class TimesheetUpdate(TimesheetBase):
    pass
