from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from routers.auth import auth as auth_router
from routers.user import user as user_router
from routers.admin import admin as admin_router

from routers.project import project_prime as project_prime_router
from routers.project import project as project_router

from routers.epic import epic as epic_router
from routers.epic import epic_prime as epic_prime_router
# from routers.task import task as task_router
# from routers.subtask import subtask as subtask_route
# from routers.sprint import sprint as sprint_route

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
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
 
 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    result = list(
        map(
            lambda error: {"message": error.get("msg"), "field": error["loc"][1] if len(error["loc"]) > 1 else "unknown", "full_error": str(error)},
            exc.args[0],
        )
    )
    return JSONResponse(status_code=422, content=result)
 
@app.exception_handler(Exception)
async def validation_exception_handler(request, exc):
    print(exc)
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

# Include the auth router
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)

app.include_router(project_prime_router)
app.include_router(project_router)

app.include_router(epic_prime_router)
app.include_router(epic_router)
# app.include_router(task_router)
# app.include_router(subtask_route)
# app.include_router(sprint_route)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
