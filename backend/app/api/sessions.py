# FILE: backend/app/api/sessions.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: REST API endpoints for session management
#   SCOPE: Active sessions, terminate, bulk operations
#   DEPENDS: M-BE-AUTH, M-BE-1C-RAC, M-BE-CACHE
#   LINKS: M-BE-API-SESSIONS
# END_MODULE_CONTRACT

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from app.database.models import User
from app.auth.dependencies import get_current_user, require_operator
from app.rac import get_rac_client, RacClient
from app.cache import cache_get, cache_set, cache_delete
from app.websocket import broadcast_event

router = APIRouter(prefix="/sessions", tags=["Sessions"])


class SessionListResponse(BaseModel):
    items: list[dict]
    total: int


class BulkTerminateRequest(BaseModel):
    cluster_id: str
    database_id: Optional[str] = None
    session_ids: Optional[list[str]] = None


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    cluster_id: str = Query(..., description="Cluster ID"),
    database_id: Optional[str] = Query(None, description="Filter by database ID"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    _: Annotated[User, Depends(get_current_user)] = None,
):
    cache_key = f"sessions:list:{cluster_id}:{database_id or 'all'}"
    cached = await cache_get(cache_key)
    if cached:
        return SessionListResponse(**cached)
    
    sessions = await rac.get_sessions_list(cluster_id, database_id)
    items = [s.model_dump() for s in sessions]
    result = SessionListResponse(items=items, total=len(items))
    
    await cache_set(cache_key, result.model_dump(), ttl=5)
    return result


@router.delete("/{session_id}")
async def terminate_session(
    session_id: str,
    cluster_id: str = Query(..., description="Cluster ID"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    current_user: Annotated[User, Depends(require_operator)] = None,
):
    await rac.terminate_session(session_id, cluster_id)
    
    await cache_delete(f"sessions:list:{cluster_id}:all")
    
    await broadcast_event(
        "session_terminated",
        {
            "session_id": session_id,
            "cluster_id": cluster_id,
            "user": current_user.username,
        },
    )
    
    return {"message": "Session terminated successfully"}


@router.post("/bulk-terminate")
async def bulk_terminate_sessions(
    request: BulkTerminateRequest,
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    current_user: Annotated[User, Depends(require_operator)] = None,
):
    terminated_count = 0
    
    if request.session_ids:
        for session_id in request.session_ids:
            try:
                await rac.terminate_session(session_id, request.cluster_id)
                terminated_count += 1
            except Exception:
                pass
    else:
        await rac.terminate_all_sessions(request.cluster_id, request.database_id)
        sessions = await rac.get_sessions_list(request.cluster_id, request.database_id)
        terminated_count = len(sessions)
    
    await cache_delete(f"sessions:list:{request.cluster_id}:all")
    if request.database_id:
        await cache_delete(f"sessions:list:{request.cluster_id}:{request.database_id}")
    
    await broadcast_event(
        "sessions_bulk_terminated",
        {
            "cluster_id": request.cluster_id,
            "database_id": request.database_id,
            "count": terminated_count,
            "user": current_user.username,
        },
    )
    
    return {
        "message": "Sessions terminated successfully",
        "terminated_count": terminated_count,
    }
