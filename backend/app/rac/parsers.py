# FILE: backend/app/rac/parsers.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Parse output from rac CLI commands into structured data
#   SCOPE: Parsers for cluster, server, database, session, log outputs
#   DEPENDS: None
#   LINKS: M-BE-1C-RAC
# END_MODULE_CONTRACT

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ClusterInfo(BaseModel):
    cluster_id: str
    cluster_name: str
    host: str
    port: int
    cluster_status: str
    processes_count: int
    memory_size: int
    selection_size: int
    sessions_limit: int
    sessions_count: int
    memory_limit: int
    security_level: int
    load_balancing_mode: str
    errors_count: int


class ServerInfo(BaseModel):
    server_id: str
    server_name: str
    host: str
    port: int
    server_status: str
    processes_count: int
    memory_size: int
    selection_size: int
    sessions_count: int
    is_main: bool
    cluster_peers: list[str] = []


class ProcessInfo(BaseModel):
    process_id: str
    server_id: str
    host: str
    port: int
    process_status: str
    memory_size: int
    sessions_count: int
    connections_count: int
    started_at: Optional[datetime] = None


class DatabaseInfo(BaseModel):
    database_id: str
    database_name: str
    dbms: str
    db_server: str
    db_name: str
    db_user: str
    db_password_masked: str
    description: str
    security_profile_name: str
    sessions_count: int
    blocked: bool
    denied_message: str


class SessionInfo(BaseModel):
    session_id: str
    database_id: str
    database_name: str
    user_name: str
    host: str
    app_id: str
    session_start: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    session_status: str
    blocked_by_dbms: bool
    locale: str
    process_id: str


class LogEntry(BaseModel):
    log_id: str
    datetime: Optional[datetime] = None
    transaction: str
    user_name: str
    computer_name: str
    app_id: str
    event: str
    severity: str
    database_name: str
    session_id: str
    transaction_id: str
    text: str


def parse_cluster_output(output: str) -> Optional[ClusterInfo]:
    lines = output.strip().split("\n")
    data = {}
    
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
    
    if not data:
        return None
    
    return ClusterInfo(
        cluster_id=data.get("cluster", ""),
        cluster_name=data.get("cluster_name", ""),
        host=data.get("host", ""),
        port=int(data.get("port", 0)),
        cluster_status=data.get("cluster_status", "unknown"),
        processes_count=int(data.get("processes_count", 0)),
        memory_size=int(data.get("memory_size", 0)),
        selection_size=int(data.get("selection_size", 0)),
        sessions_limit=int(data.get("sessions_limit", 0)),
        sessions_count=int(data.get("sessions_count", 0)),
        memory_limit=int(data.get("memory_limit", 0)),
        security_level=int(data.get("security_level", 0)),
        load_balancing_mode=data.get("load_balancing_mode", ""),
        errors_count=int(data.get("errors_count", 0)),
    )


def parse_servers_output(output: str) -> list[ServerInfo]:
    servers = []
    blocks = output.strip().split("\n\n")
    
    for block in blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split("\n")
        data = {}
        
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
        
        if data.get("server"):
            servers.append(ServerInfo(
                server_id=data.get("server", ""),
                server_name=data.get("server_name", ""),
                host=data.get("host", ""),
                port=int(data.get("port", 0)),
                server_status=data.get("server_status", "unknown"),
                processes_count=int(data.get("processes_count", 0)),
                memory_size=int(data.get("memory_size", 0)),
                selection_size=int(data.get("selection_size", 0)),
                sessions_count=int(data.get("sessions_count", 0)),
                is_main=data.get("is_main", "").lower() in ("yes", "true", "1"),
                cluster_peers=data.get("cluster_peers", "").split(",") if data.get("cluster_peers") else [],
            ))
    
    return servers


def parse_processes_output(output: str) -> list[ProcessInfo]:
    processes = []
    blocks = output.strip().split("\n\n")
    
    for block in blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split("\n")
        data = {}
        
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
        
        if data.get("process"):
            started_at = None
            if data.get("started_at"):
                try:
                    started_at = datetime.strptime(data["started_at"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
            
            processes.append(ProcessInfo(
                process_id=data.get("process", ""),
                server_id=data.get("server", ""),
                host=data.get("host", ""),
                port=int(data.get("port", 0)),
                process_status=data.get("process_status", "unknown"),
                memory_size=int(data.get("memory_size", 0)),
                sessions_count=int(data.get("sessions_count", 0)),
                connections_count=int(data.get("connections_count", 0)),
                started_at=started_at,
            ))
    
    return processes


def parse_databases_output(output: str) -> list[DatabaseInfo]:
    databases = []
    blocks = output.strip().split("\n\n")
    
    for block in blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split("\n")
        data = {}
        
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
        
        if data.get("infobase"):
            databases.append(DatabaseInfo(
                database_id=data.get("infobase", ""),
                database_name=data.get("infobase_name", ""),
                dbms=data.get("dbms", ""),
                db_server=data.get("db_server", ""),
                db_name=data.get("db_name", ""),
                db_user=data.get("db_user", ""),
                db_password_masked="***",
                description=data.get("description", ""),
                security_profile_name=data.get("security_profile_name", ""),
                sessions_count=int(data.get("sessions_count", 0)),
                blocked=data.get("blocked", "").lower() in ("yes", "true", "1"),
                denied_message=data.get("denied_message", ""),
            ))
    
    return databases


def parse_sessions_output(output: str) -> list[SessionInfo]:
    sessions = []
    blocks = output.strip().split("\n\n")
    
    for block in blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split("\n")
        data = {}
        
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
        
        if data.get("session"):
            session_start = None
            last_active_at = None
            
            for field, val in [("session_start", session_start), ("last_active_at", last_active_at)]:
                if data.get(field):
                    try:
                        data[field] = datetime.strptime(data[field], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        data[field] = None
            
            sessions.append(SessionInfo(
                session_id=data.get("session", ""),
                database_id=data.get("infobase", ""),
                database_name=data.get("infobase_name", ""),
                user_name=data.get("user_name", ""),
                host=data.get("host", ""),
                app_id=data.get("app_id", ""),
                session_start=data.get("session_start"),
                last_active_at=data.get("last_active_at"),
                session_status=data.get("session_status", "unknown"),
                blocked_by_dbms=data.get("blocked_by_dbms", "").lower() in ("yes", "true", "1"),
                locale=data.get("locale", ""),
                process_id=data.get("process", ""),
            ))
    
    return sessions


def parse_logs_output(output: str) -> list[LogEntry]:
    logs = []
    blocks = output.strip().split("\n\n")
    
    for block in blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split("\n")
        data = {}
        
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
        
        if data:
            log_datetime = None
            if data.get("datetime"):
                try:
                    log_datetime = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
            
            logs.append(LogEntry(
                log_id=data.get("log_id", ""),
                datetime=log_datetime,
                transaction=data.get("transaction", ""),
                user_name=data.get("user_name", ""),
                computer_name=data.get("computer_name", ""),
                app_id=data.get("app_id", ""),
                event=data.get("event", ""),
                severity=data.get("severity", ""),
                database_name=data.get("infobase_name", ""),
                session_id=data.get("session", ""),
                transaction_id=data.get("transaction_id", ""),
                text=data.get("text", ""),
            ))
    
    return logs
