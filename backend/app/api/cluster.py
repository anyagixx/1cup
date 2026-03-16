# FILE: backend/app/api/cluster.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: REST API endpoints for cluster management
#   SCOPE: Cluster info, status, settings
#   DEPENDS: M-BE-AUTH, M-BE-1C-RAC, M-BE-CACHE
#   LINKS: M-BE-API-CLUSTER
# END_MODULE_CONTRACT

from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.database.models import User
from app.auth.dependencies import get_current_user, require_operator
from app.rac import get_rac_client, RacClient
from app.cache import cache_get, cache_set

router = APIRouter(prefix="/cluster", tags=["Cluster"])


class ClusterStatusResponse(BaseModel):
    cluster_id: str
    status: str
    servers_count: int
    databases_count: int
    sessions_count: int
    processes_count: int
    memory_used: int
    memory_limit: int


@router.get("/list")
async def list_clusters(
    rac: Annotated[RacClient, Depends(get_rac_client)],
    _: Annotated[User, Depends(get_current_user)],
):
    cache_key = "cluster:list"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    clusters = await rac.get_cluster_list()
    await cache_set(cache_key, clusters, ttl=60)
    return clusters


@router.get("/info/{cluster_id}")
async def get_cluster_info(
    cluster_id: str,
    rac: Annotated[RacClient, Depends(get_rac_client)],
    _: Annotated[User, Depends(get_current_user)],
):
    cache_key = f"cluster:info:{cluster_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    info = await rac.get_cluster_info(cluster_id)
    if info:
        result = info.model_dump()
        await cache_set(cache_key, result, ttl=30)
        return result
    return None


@router.get("/status/{cluster_id}", response_model=ClusterStatusResponse)
async def get_cluster_status(
    cluster_id: str,
    rac: Annotated[RacClient, Depends(get_rac_client)],
    _: Annotated[User, Depends(get_current_user)],
):
    cache_key = f"cluster:status:{cluster_id}"
    cached = await cache_get(cache_key)
    if cached:
        return ClusterStatusResponse(**cached)
    
    cluster_info = await rac.get_cluster_info(cluster_id)
    servers = await rac.get_servers_list(cluster_id)
    databases = await rac.get_databases_list(cluster_id)
    sessions = await rac.get_sessions_list(cluster_id)
    
    total_memory = sum(s.memory_size for s in servers)
    total_processes = sum(s.processes_count for s in servers)
    
    status = ClusterStatusResponse(
        cluster_id=cluster_id,
        status=cluster_info.cluster_status if cluster_info else "unknown",
        servers_count=len(servers),
        databases_count=len(databases),
        sessions_count=len(sessions),
        processes_count=total_processes,
        memory_used=total_memory,
        memory_limit=cluster_info.memory_limit if cluster_info else 0,
    )
    
    await cache_set(cache_key, status.model_dump(), ttl=10)
    return status
