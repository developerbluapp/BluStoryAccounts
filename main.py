# main.py
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from blustorymicroservices.BluStoryAccounts.routers import members,auth, operators,admin,organisations
from blustorymicroservices.BluStoryAccounts.models.exceptions import AppException
from fastapi.exceptions import RequestValidationError
from starlette import status
import logging

app = FastAPI(
    title="BluStory App License Holders Service",
    description="Manage license holders and their associated members"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app.include_router(members.router)
app.include_router(operators.router)
app.include_router(organisations.router)
app.include_router(auth.operator.router)
app.include_router(auth.member.router)
app.include_router(auth.organisation.router)
app.include_router(admin.operators.router)
app.include_router(admin.organisations.router)

# main.py
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message, "status": exc.status}}
    )
# 2. Pydantic / request body / query / path validation failures (very common)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # You can make this nicer than the default ugly list
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "status": 422,
                "details": errors
            }
        }
    )

# 3. FastAPI/Starlette HTTPException (when someone raises HTTPException(status_code=403, detail="Forbidden"))
# Note: register for starlette.exceptions.HTTPException, not fastapi.HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "status": exc.status_code
            }
        },
        headers=exc.headers if exc.headers else None
    )


@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        msg=f"UNHANDLED EXCEPTION | {request.method} {request.url} | {type(exc).__name__}",
        exc_info=True,
    )
    IS_DEVELOPMENT = os.getenv("ENVIRONMENT", "").lower() == "development"

    if IS_DEVELOPMENT:
        import traceback
        tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"{type(exc).__name__}: {str(exc)}",
                    "status": 500,
                    "path": f"{request.method} {request.url}",
                    "traceback": tb_lines,           # list of strings
                    "detail": "Full traceback available in development"
                }
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred.",
                    "status": 500
                }
            }
        )
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
