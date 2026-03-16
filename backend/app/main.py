# FILE: backend/app/main.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: FastAPI application entry point
#   SCOPE: App initialization, middleware, routers, lifecycle
#   DEPENDS: All backend modules
#   LINKS: M-BE-*
# END_MODULE_CONTRACT

import uuid
from contextlib import asynccontextmanager
from typing import Callable
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.logging_config import setup_logging, get_logger, request_context
from app.exceptions import AppException
from app.database import init_db, close_db
from app.cache import redis_client
from app.auth import auth_router
from app.api import api_router
from app.websocket import websocket_endpoint

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting 1C Web Console API")
    
    await init_db()
    logger.info("Database initialized")
    
    await redis_client.connect()
    logger.info("Redis connected")
    
    yield
    
    logger.info("Shutting down 1C Web Console API")
    await redis_client.disconnect()
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Web console for 1C:Enterprise cluster management",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next: Callable):
    request_id = str(uuid.uuid4())[:8]
    
    with request_context(request_id):
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"method": request.method, "path": request.url.path},
        )
        
        response = await call_next(request)
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
        )
        
        return response


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
            }
        },
    )


app.include_router(auth_router, prefix="/api")
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws/{connection_id}")
async def websocket_route(websocket, connection_id: str):
    await websocket_endpoint(websocket, connection_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
