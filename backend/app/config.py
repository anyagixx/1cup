# FILE: backend/app/config.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Application configuration management using Pydantic Settings
#   SCOPE: Environment variables, default values, validation
#   DEPENDS: None
#   LINKS: M-BE-CORE
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   Settings - Main configuration class with all app settings
#   get_settings - Singleton getter for settings instance
# END_MODULE_MAP

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "1C Web Console"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "change-me-in-production-with-secure-random-string"
    
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/1c_console"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 300
    
    jwt_secret_key: str = "change-me-in-production-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    rac_executable: str = "/opt/1cv8/x86_64/8.3.23.1739/rac"
    rac_cluster_host: str = "localhost"
    rac_cluster_port: int = 1545
    rac_cluster_user: str = ""
    rac_cluster_password: str = ""
    
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    log_level: str = "INFO"
    log_format: str = "json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
