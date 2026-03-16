# API package
from fastapi import APIRouter

from app.api.cluster import router as cluster_router
from app.api.servers import router as servers_router
from app.api.databases import router as databases_router
from app.api.sessions import router as sessions_router
from app.api.logs import router as logs_router

api_router = APIRouter()
api_router.include_router(cluster_router, prefix="/api")
api_router.include_router(servers_router, prefix="/api")
api_router.include_router(databases_router, prefix="/api")
api_router.include_router(sessions_router, prefix="/api")
api_router.include_router(logs_router, prefix="/api")
