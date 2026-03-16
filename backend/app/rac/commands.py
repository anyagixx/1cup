# FILE: backend/app/rac/commands.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Define rac CLI command builders
#   SCOPE: Command templates for cluster, server, database, session operations
#   DEPENDS: None
#   LINKS: M-BE-1C-RAC
# END_MODULE_CONTRACT

from typing import Optional
from dataclasses import dataclass


@dataclass
class RacCommand:
    executable: str
    subcommand: str
    args: dict
    
    def build(self) -> list[str]:
        cmd = [self.executable, self.subcommand]
        
        for key, value in self.args.items():
            if value is None:
                continue
            if isinstance(value, bool):
                if value:
                    cmd.append(f"--{key}")
            else:
                cmd.extend([f"--{key}", str(value)])
        
        return cmd


class RacCommandBuilder:
    def __init__(self, executable: str, cluster_host: str, cluster_port: int):
        self.executable = executable
        self.cluster_host = cluster_host
        self.cluster_port = cluster_port
    
    def _base_args(self) -> dict:
        return {
            "cluster-host": self.cluster_host,
            "cluster-port": self.cluster_port,
        }
    
    def cluster_info(self, cluster_id: str) -> RacCommand:
        return RacCommand(
            executable=self.executable,
            subcommand="cluster",
            args={**self._base_args(), "cluster": cluster_id},
        )
    
    def cluster_list(self) -> RacCommand:
        return RacCommand(
            executable=self.executable,
            subcommand="cluster",
            args=self._base_args(),
        )
    
    def server_list(self, cluster_id: str) -> RacCommand:
        return RacCommand(
            executable=self.executable,
            subcommand="server",
            args={**self._base_args(), "cluster": cluster_id},
        )
    
    def server_info(self, server_id: str, cluster_id: str) -> RacCommand:
        return RacCommand(
            executable=self.executable,
            subcommand="server",
            args={**self._base_args(), "cluster": cluster_id, "server": server_id},
        )
    
    def process_list(self, cluster_id: str, server_id: Optional[str] = None) -> RacCommand:
        args = {**self._base_args(), "cluster": cluster_id}
        if server_id:
            args["server"] = server_id
        return RacCommand(
            executable=self.executable,
            subcommand="process",
            args=args,
        )
    
    def database_list(self, cluster_id: str) -> RacCommand:
        return RacCommand(
            executable=self.executable,
            subcommand="infobase",
            args={**self._base_args(), "cluster": cluster_id},
        )
    
    def database_info(self, database_id: str, cluster_id: str) -> RacCommand:
        return RacCommand(
            executable=self.executable,
            subcommand="infobase",
            args={**self._base_args(), "cluster": cluster_id, "infobase": database_id},
        )
    
    def database_create(
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
    ) -> RacCommand:
        args = {
            **self._base_args(),
            "cluster": cluster_id,
            "create-infobase": "",
            "name": name,
            "dbms": dbms,
            "db-server": db_server,
            "db-name": db_name,
            "db-user": db_user,
            "db-pwd": db_password,
        }
        if description:
            args["descr"] = description
        if security_profile:
            args["security-profile-name"] = security_profile
        
        return RacCommand(
            executable=self.executable,
            subcommand="infobase",
            args=args,
        )
    
    def database_update(
        self,
        database_id: str,
        cluster_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        denied_message: Optional[str] = None,
        permission_code: Optional[str] = None,
        sessions_limit: Optional[int] = None,
    ) -> RacCommand:
        args = {
            **self._base_args(),
            "cluster": cluster_id,
            "infobase": database_id,
            "update-infobase": "",
        }
        if name:
            args["name"] = name
        if description:
            args["descr"] = description
        if denied_message:
            args["denied-message"] = denied_message
        if permission_code:
            args["permission-code"] = permission_code
        if sessions_limit:
            args["sessions-limit"] = sessions_limit
        
        return RacCommand(
            executable=self.executable,
            subcommand="infobase",
            args=args,
        )
    
    def database_delete(self, database_id: str, cluster_id: str, drop_db: bool = False) -> RacCommand:
        args = {
            **self._base_args(),
            "cluster": cluster_id,
            "infobase": database_id,
            "drop-infobase": "",
        }
        if drop_db:
            args["drop-database"] = ""
        
        return RacCommand(
            executable=self.executable,
            subcommand="infobase",
            args=args,
        )
    
    def session_list(
        self,
        cluster_id: str,
        database_id: Optional[str] = None,
    ) -> RacCommand:
        args = {**self._base_args(), "cluster": cluster_id}
        if database_id:
            args["infobase"] = database_id
        
        return RacCommand(
            executable=self.executable,
            subcommand="session",
            args=args,
        )
    
    def session_terminate(self, session_id: str, cluster_id: str) -> RacCommand:
        return RacCommand(
            executable=self.executable,
            subcommand="session",
            args={
                **self._base_args(),
                "cluster": cluster_id,
                "session": session_id,
                "terminate": "",
            },
        )
    
    def sessions_terminate_all(
        self,
        cluster_id: str,
        database_id: Optional[str] = None,
    ) -> RacCommand:
        args = {
            **self._base_args(),
            "cluster": cluster_id,
            "terminate-all": "",
        }
        if database_id:
            args["infobase"] = database_id
        
        return RacCommand(
            executable=self.executable,
            subcommand="session",
            args=args,
        )
    
    def log_list(
        self,
        cluster_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        database_id: Optional[str] = None,
    ) -> RacCommand:
        args = {**self._base_args(), "cluster": cluster_id}
        if start_time:
            args["start-time"] = start_time
        if end_time:
            args["end-time"] = end_time
        if database_id:
            args["infobase"] = database_id
        
        return RacCommand(
            executable=self.executable,
            subcommand="log",
            args=args,
        )
