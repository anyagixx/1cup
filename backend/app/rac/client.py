# FILE: backend/app/rac/client.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Execute rac CLI commands and return parsed results
#   SCOPE: Async subprocess execution, error handling, result parsing
#   DEPENDS: M-BE-CORE (config, exceptions), M-BE-1C-RAC (commands, parsers)
#   LINKS: M-BE-1C-RAC
# END_MODULE_CONTRACT

import asyncio
from typing import Optional
from datetime import datetime

from app.config import get_settings
from app.exceptions import RacCommandException
from app.rac.commands import RacCommandBuilder
from app.rac.parsers import (
    parse_cluster_output,
    parse_servers_output,
    parse_processes_output,
    parse_databases_output,
    parse_sessions_output,
    parse_logs_output,
    ClusterInfo,
    ServerInfo,
    ProcessInfo,
    DatabaseInfo,
    SessionInfo,
    LogEntry,
)

settings = get_settings()


class RacClient:
    def __init__(
        self,
        executable: Optional[str] = None,
        cluster_host: Optional[str] = None,
        cluster_port: Optional[int] = None,
    ):
        self.executable = executable or settings.rac_executable
        self.cluster_host = cluster_host or settings.rac_cluster_host
        self.cluster_port = cluster_port or settings.rac_cluster_port
        self.builder = RacCommandBuilder(
            self.executable,
            self.cluster_host,
            self.cluster_port,
        )
    
    async def _execute_command(self, command: list[str]) -> str:
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30.0
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode("utf-8", errors="replace").strip()
                raise RacCommandException(
                    command=" ".join(command),
                    message=f"RAC command failed: {error_msg}",
                    details={"return_code": process.returncode, "stderr": error_msg},
                )
            
            return stdout.decode("utf-8", errors="replace")
        
        except asyncio.TimeoutError:
            raise RacCommandException(
                command=" ".join(command),
                message="RAC command timed out",
            )
        except FileNotFoundError:
            raise RacCommandException(
                command=" ".join(command),
                message=f"RAC executable not found: {self.executable}",
            )
    
    async def get_cluster_list(self) -> list[dict]:
        cmd = self.builder.cluster_list()
        output = await self._execute_command(cmd.build())
        return [{"cluster_id": line.split(":")[1].strip()} for line in output.strip().split("\n") if ":" in line]
    
    async def get_cluster_info(self, cluster_id: str) -> Optional[ClusterInfo]:
        cmd = self.builder.cluster_info(cluster_id)
        output = await self._execute_command(cmd.build())
        return parse_cluster_output(output)
    
    async def get_servers_list(self, cluster_id: str) -> list[ServerInfo]:
        cmd = self.builder.server_list(cluster_id)
        output = await self._execute_command(cmd.build())
        return parse_servers_output(output)
    
    async def get_server_info(self, server_id: str, cluster_id: str) -> Optional[ServerInfo]:
        cmd = self.builder.server_info(server_id, cluster_id)
        output = await self._execute_command(cmd.build())
        servers = parse_servers_output(output)
        return servers[0] if servers else None
    
    async def get_processes_list(
        self,
        cluster_id: str,
        server_id: Optional[str] = None,
    ) -> list[ProcessInfo]:
        cmd = self.builder.process_list(cluster_id, server_id)
        output = await self._execute_command(cmd.build())
        return parse_processes_output(output)
    
    async def get_databases_list(self, cluster_id: str) -> list[DatabaseInfo]:
        cmd = self.builder.database_list(cluster_id)
        output = await self._execute_command(cmd.build())
        return parse_databases_output(output)
    
    async def get_database_info(
        self,
        database_id: str,
        cluster_id: str,
    ) -> Optional[DatabaseInfo]:
        cmd = self.builder.database_info(database_id, cluster_id)
        output = await self._execute_command(cmd.build())
        databases = parse_databases_output(output)
        return databases[0] if databases else None
    
    async def create_database(
        self,
        cluster_id: str,
        name: str,
        dbms: str,
        db_server: str,
        db_name: str,
        db_user: str,
        db_password: str,
        description: Optional[str] = None,
        security_profile: Optional[str] = None,
    ) -> str:
        cmd = self.builder.database_create(
            cluster_id=cluster_id,
            name=name,
            dbms=dbms,
            db_server=db_server,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            description=description,
            security_profile=security_profile,
        )
        output = await self._execute_command(cmd.build())
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                if key.strip().lower() == "infobase":
                    return value.strip()
        return ""
    
    async def update_database(
        self,
        database_id: str,
        cluster_id: str,
        **kwargs,
    ) -> bool:
        cmd = self.builder.database_update(database_id, cluster_id, **kwargs)
        await self._execute_command(cmd.build())
        return True
    
    async def delete_database(
        self,
        database_id: str,
        cluster_id: str,
        drop_db: bool = False,
    ) -> bool:
        cmd = self.builder.database_delete(database_id, cluster_id, drop_db)
        await self._execute_command(cmd.build())
        return True
    
    async def get_sessions_list(
        self,
        cluster_id: str,
        database_id: Optional[str] = None,
    ) -> list[SessionInfo]:
        cmd = self.builder.session_list(cluster_id, database_id)
        output = await self._execute_command(cmd.build())
        return parse_sessions_output(output)
    
    async def terminate_session(self, session_id: str, cluster_id: str) -> bool:
        cmd = self.builder.session_terminate(session_id, cluster_id)
        await self._execute_command(cmd.build())
        return True
    
    async def terminate_all_sessions(
        self,
        cluster_id: str,
        database_id: Optional[str] = None,
    ) -> bool:
        cmd = self.builder.sessions_terminate_all(cluster_id, database_id)
        await self._execute_command(cmd.build())
        return True
    
    async def get_logs(
        self,
        cluster_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        database_id: Optional[str] = None,
    ) -> list[LogEntry]:
        cmd = self.builder.log_list(
            cluster_id=cluster_id,
            start_time=start_time.strftime("%Y-%m-%d %H:%M:%S") if start_time else None,
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else None,
            database_id=database_id,
        )
        output = await self._execute_command(cmd.build())
        return parse_logs_output(output)


rac_client = RacClient()


def get_rac_client() -> RacClient:
    return rac_client
