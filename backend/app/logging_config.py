# FILE: backend/app/logging_config.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Structured logging configuration for the application
#   SCOPE: Log formatters, handlers, logger setup
#   DEPENDS: M-BE-CORE (config)
#   LINKS: M-BE-CORE
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   setup_logging - Configure application logging
#   get_logger - Get configured logger instance
#   RequestLogger - Context manager for request logging
# END_MODULE_MAP

import logging
import sys
import json
from datetime import datetime
from typing import Any
from contextvars import ContextVar
from contextlib import contextmanager

from app.config import get_settings

settings = get_settings()
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        extra = getattr(record, "extra", None)
        if extra:
            log_data["extra"] = extra
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.utcnow().isoformat() + "Z"
        request_id = request_id_var.get()
        request_part = f" [{request_id}]" if request_id else ""
        
        base = f"{timestamp}{request_part} | {record.levelname:8} | {record.name}:{record.lineno} | {record.getMessage()}"
        
        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"
        
        return base


def setup_logging() -> None:
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


@contextmanager
def request_context(request_id: str):
    token = request_id_var.set(request_id)
    try:
        yield
    finally:
        request_id_var.reset(token)
