# server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from routers.auth import router as auth_router
from routers.project import project as project_router
from routers.epic import epic as epic_router

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
            lambda error: {"message": error["msg"], "field": error["loc"][1]},
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
app.include_router(project_router)
app.include_router(epic_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
