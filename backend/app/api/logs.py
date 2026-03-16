# FILE: backend/app/api/logs.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: REST API endpoints for log viewing
#   SCOPE: Log list, filters, export
#   DEPENDS: M-BE-AUTH, M-BE-1C-RAC
#   LINKS: M-BE-API-LOGS
# END_MODULE_CONTRACT

from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import csv

from app.database.models import User
from app.auth.dependencies import get_current_user
from app.rac import get_rac_client, RacClient
from app.cache import cache_get, cache_set

router = APIRouter(prefix="/logs", tags=["Logs"])


class LogListResponse(BaseModel):
    items: list[dict]
    total: int


@router.get("", response_model=LogListResponse)
async def list_logs(
    cluster_id: str = Query(..., description="Cluster ID"),
    database_id: Optional[str] = Query(None, description="Filter by database ID"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    _: Annotated[User, Depends(get_current_user)] = None,
):
    cache_key = f"logs:list:{cluster_id}:{database_id or 'all'}:{start_time}:{end_time}"
    cached = await cache_get(cache_key)
    if cached:
        return LogListResponse(**cached)
    
    logs = await rac.get_logs(
        cluster_id=cluster_id,
        start_time=start_time,
        end_time=end_time,
        database_id=database_id,
    )
    
    items = [log.model_dump() for log in logs]
    result = LogListResponse(items=items, total=len(items))
    
    await cache_set(cache_key, result.model_dump(), ttl=10)
    return result


@router.get("/export")
async def export_logs(
    cluster_id: str = Query(..., description="Cluster ID"),
    database_id: Optional[str] = Query(None, description="Filter by database ID"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    format: str = Query("csv", pattern="^(csv|json)$"),
    rac: Annotated[RacClient, Depends(get_rac_client)] = None,
    _: Annotated[User, Depends(get_current_user)] = None,
):
    logs = await rac.get_logs(
        cluster_id=cluster_id,
        start_time=start_time,
        end_time=end_time,
        database_id=database_id,
    )
    
    if format == "json":
        import json
        content = json.dumps([log.model_dump() for log in logs], indent=2, default=str)
        return StreamingResponse(
            iter([content]),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            },
        )
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "datetime", "event", "severity", "user_name", "computer_name",
        "database_name", "session_id", "transaction_id", "text"
    ])
    
    for log in logs:
        writer.writerow([
            log.datetime.isoformat() if log.datetime else "",
            log.event,
            log.severity,
            log.user_name,
            log.computer_name,
            log.database_name,
            log.session_id,
            log.transaction_id,
            log.text,
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )
