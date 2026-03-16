# FILE: backend/app/api/databases.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: REST API endpoints for database management
#   SCOPE: CRUD operations, backup
#   DEPENDS: M-BE-AUTH, M-BE-1C-RAC, M-BE-DB, M-BE-CACHE
#   LINKS: M-BE-API-DBS
# END_MODULE_CONTRACT

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from app.database.models import User
from app.database.schemas import PaginatedResponse
from app.auth.dependencies import get_current_user, require_operator, require_admin
from app.rac import get_rac_client, RacClient
from app.cache import cache_get, cache_set, cache_delete
from app.websocket import broadcast_event

router = APIRouter(prefix="/databases", tags=["Databases"])


class DatabaseCreateRequest(BaseModel):
    cluster_id: str
    name: str = Field(..., min_length=1, max_length=100)
    dbms: str = Field(default="PostgreSQL", pattern="^(PostgreSQL|MSSQL|MySQL|IBMDB2|Oracle)$")
    db_server: str
    db_name: str
    db_user: str
    db_password: str
    description: Optional[str] = None
    security_profile: Optional[str] = None


class DatabaseUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    denied_message: Optional[str] = None
    permission_code: Optional[str] = None
    sessions_limit: Optional[int] = None


class DatabaseListResponse(BaseModel):
    items: list[dict]
    total: int


@router.get("", response_model=DatabaseListResponse)
async def list_databases(
    cluster_id: str = Query(..., description="Cluster ID"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    _: Annotated[User, Depends(get_current_user)] = None,
):
    cache_key = f"databases:list:{cluster_id}"
    cached = await cache_get(cache_key)
    if cached:
        return DatabaseListResponse(**cached)
    
    databases = await rac.get_databases_list(cluster_id)
    items = [d.model_dump() for d in databases]
    result = DatabaseListResponse(items=items, total=len(items))
    
    await cache_set(cache_key, result.model_dump(), ttl=30)
    return result


@router.get("/{database_id}")
async def get_database_info(
    database_id: str,
    cluster_id: str = Query(..., description="Cluster ID"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    _: Annotated[User, Depends(get_current_user)] = None,
):
    cache_key = f"databases:info:{cluster_id}:{database_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    database = await rac.get_database_info(database_id, cluster_id)
    if database:
        result = database.model_dump()
        await cache_set(cache_key, result, ttl=30)
        return result
    return None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_database(
    request: DatabaseCreateRequest,
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    current_user: Annotated[User, Depends(require_admin)] = None,
):
    database_id = await rac.create_database(
        cluster_id=request.cluster_id,
        name=request.name,
        dbms=request.dbms,
        db_server=request.db_server,
        db_name=request.db_name,
        db_user=request.db_user,
        db_password=request.db_password,
        description=request.description,
        security_profile=request.security_profile,
    )
    
    await cache_delete(f"databases:list:{request.cluster_id}")
    
    await broadcast_event(
        "database_created",
        {
            "database_id": database_id,
            "name": request.name,
            "cluster_id": request.cluster_id,
            "user": current_user.username,
        },
    )
    
    return {
        "message": "Database created successfully",
        "database_id": database_id,
    }


@router.put("/{database_id}")
async def update_database(
    database_id: str,
    request: DatabaseUpdateRequest,
    cluster_id: str = Query(..., description="Cluster ID"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    current_user: Annotated[User, Depends(require_operator)] = None,
):
    update_data = request.model_dump(exclude_unset=True)
    
    await rac.update_database(
        database_id=database_id,
        cluster_id=cluster_id,
        **update_data,
    )
    
    await cache_delete(f"databases:info:{cluster_id}:{database_id}")
    await cache_delete(f"databases:list:{cluster_id}")
    
    await broadcast_event(
        "database_updated",
        {
            "database_id": database_id,
            "cluster_id": cluster_id,
            "changes": update_data,
            "user": current_user.username,
        },
    )
    
    return {"message": "Database updated successfully"}


@router.delete("/{database_id}")
async def delete_database(
    database_id: str,
    cluster_id: str = Query(..., description="Cluster ID"),
    drop_db: bool = Query(False, description="Also drop the physical database"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    current_user: Annotated[User, Depends(require_admin)] = None,
):
    await rac.delete_database(database_id, cluster_id, drop_db)
    
    await cache_delete(f"databases:info:{cluster_id}:{database_id}")
    await cache_delete(f"databases:list:{cluster_id}")
    
    await broadcast_event(
        "database_deleted",
        {
            "database_id": database_id,
            "cluster_id": cluster_id,
            "drop_db": drop_db,
            "user": current_user.username,
        },
    )
    
    return {"message": "Database deleted successfully"}
