# FILE: backend/app/exceptions.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Custom exception hierarchy for the application
#   SCOPE: Base exceptions, HTTP exceptions, domain-specific exceptions
#   DEPENDS: None
#   LINKS: M-BE-CORE
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   AppException - Base exception class for all application exceptions
#   AuthenticationException - Raised when authentication fails
#   AuthorizationException - Raised when user lacks permissions
#   NotFoundException - Raised when resource is not found
#   ValidationException - Raised when validation fails
#   RacCommandException - Raised when rac command fails
#   DatabaseException - Raised when database operation fails
#   CacheException - Raised when cache operation fails
# END_MODULE_MAP

from typing import Any, Optional


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class AuthenticationException(AppException):
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details,
        )


class AuthorizationException(AppException):
    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
        )


class NotFoundException(AppException):
    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ValidationException(AppException):
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class RacCommandException(AppException):
    def __init__(
        self,
        command: str = "",
        message: str = "RAC command execution failed",
        details: Optional[dict[str, Any]] = None,
    ):
        error_details = details or {}
        if command:
            error_details["command"] = command
        super().__init__(
            message=message,
            code="RAC_COMMAND_ERROR",
            status_code=500,
            details=error_details,
        )


class DatabaseException(AppException):
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details,
        )


class CacheException(AppException):
    def __init__(
        self,
        message: str = "Cache operation failed",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="CACHE_ERROR",
            status_code=500,
            details=details,
        )
