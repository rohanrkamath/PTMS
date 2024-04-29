from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

import re

from routers.auth import auth as auth_router
from routers.user import user as user_router
from routers.admin import admin as admin_router
from routers.project import project_prime as project_prime_router, project as project_router
from routers.epic import epic as epic_router, epic_prime as epic_prime_router
from routers.task import task as task_router
from routers.subtask import subtask as subtask_route
from routers.sprint import sprint as sprint_route
from routers.timesheet import timesheet_prime as timesheet_prime_router, timesheet as timesheet_router

app = FastAPI()

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        error_msg = error['msg']
        field = error['loc'][-1]  # The field involved in the validation error
        error_type = error['type']
        
        # Custom handling for enum errors
        if error_type == 'type_error.enum' or 'value_error.enum' in error_type:
            # Attempt to extract expected values if mentioned in the error message
            expected_values = re.findall(r"expected: (.*)", error_msg)
            expected_values = expected_values[0] if expected_values else "specific values"
            error_msg = f"Invalid value for {field}. Expected one of: {expected_values}"

        errors.append({"field": field, "message": error_msg})
    
    return JSONResponse(status_code=422, content={"detail": errors})

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail if exc.detail else "An error occurred"})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(project_prime_router)
app.include_router(project_router)
app.include_router(epic_prime_router)
app.include_router(epic_router)
app.include_router(task_router)
app.include_router(subtask_route)
app.include_router(sprint_route)
app.include_router(timesheet_prime_router)
app.include_router(timesheet_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
