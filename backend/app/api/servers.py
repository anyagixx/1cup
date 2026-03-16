# FILE: backend/app/api/servers.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: REST API endpoints for server management
#   SCOPE: Server list, details, processes, restart
#   DEPENDS: M-BE-AUTH, M-BE-1C-RAC, M-BE-CACHE
#   LINKS: M-BE-API-SERVERS
# END_MODULE_CONTRACT

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.database.models import User
from app.auth.dependencies import get_current_user, require_operator
from app.rac import get_rac_client, RacClient
from app.cache import cache_get, cache_set

router = APIRouter(prefix="/servers", tags=["Servers"])


class ServerListResponse(BaseModel):
    items: list[dict]
    total: int


class ProcessListResponse(BaseModel):
    items: list[dict]
    total: int


@router.get("", response_model=ServerListResponse)
async def list_servers(
    cluster_id: str = Query(..., description="Cluster ID"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    _: Annotated[User, Depends(get_current_user)] = None,
):
    cache_key = f"servers:list:{cluster_id}"
    cached = await cache_get(cache_key)
    if cached:
        return ServerListResponse(**cached)
    
    servers = await rac.get_servers_list(cluster_id)
    items = [s.model_dump() for s in servers]
    result = ServerListResponse(items=items, total=len(items))
    
    await cache_set(cache_key, result.model_dump(), ttl=30)
    return result


@router.get("/{server_id}")
async def get_server_info(
    server_id: str,
    cluster_id: str = Query(..., description="Cluster ID"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    _: Annotated[User, Depends(get_current_user)] = None,
):
    cache_key = f"servers:info:{cluster_id}:{server_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    server = await rac.get_server_info(server_id, cluster_id)
    if server:
        result = server.model_dump()
        await cache_set(cache_key, result, ttl=30)
        return result
    return None


@router.get("/{server_id}/processes", response_model=ProcessListResponse)
async def get_server_processes(
    server_id: str,
    cluster_id: str = Query(..., description="Cluster ID"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    _: Annotated[User, Depends(get_current_user)] = None,
):
    cache_key = f"servers:processes:{cluster_id}:{server_id}"
    cached = await cache_get(cache_key)
    if cached:
        return ProcessListResponse(**cached)
    
    processes = await rac.get_processes_list(cluster_id, server_id)
    items = [p.model_dump() for p in processes]
    result = ProcessListResponse(items=items, total=len(items))
    
    await cache_set(cache_key, result.model_dump(), ttl=15)
    return result


@router.get("/all/processes", response_model=ProcessListResponse)
async def get_all_processes(
    cluster_id: str = Query(..., description="Cluster ID"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    _: Annotated[User, Depends(get_current_user)] = None,
):
    cache_key = f"processes:all:{cluster_id}"
    cached = await cache_get(cache_key)
    if cached:
        return ProcessListResponse(**cached)
    
    processes = await rac.get_processes_list(cluster_id)
    items = [p.model_dump() for p in processes]
    result = ProcessListResponse(items=items, total=len(items))
    
    await cache_set(cache_key, result.model_dump(), ttl=15)
    return result
