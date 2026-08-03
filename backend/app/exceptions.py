from __future__ import annotations

from fastapi import HTTPException


class KarigarJiException(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str):
        super().__init__(status_code=status_code, detail={"error_code": error_code, "message": message})


class NotFoundError(KarigarJiException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(404, "NOT_FOUND", f"{resource} '{resource_id}' not found")


class UnauthorizedError(KarigarJiException):
    def __init__(self):
        super().__init__(401, "UNAUTHORIZED", "Authentication required")


class ForbiddenError(KarigarJiException):
    def __init__(self):
        super().__init__(403, "FORBIDDEN", "You do not have access to this resource")


class ValidationError(KarigarJiException):
    def __init__(self, message: str):
        super().__init__(422, "VALIDATION_ERROR", message)


class AIProviderError(KarigarJiException):
    def __init__(self, provider: str, message: str):
        super().__init__(502, "AI_PROVIDER_ERROR", f"{provider}: {message}")


class StorageError(KarigarJiException):
    def __init__(self, message: str):
        super().__init__(500, "STORAGE_ERROR", message)
