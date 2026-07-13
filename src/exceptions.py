"""Custom exception classes for the DPR Agentic AI application."""

from fastapi import HTTPException, status


class DPRBaseError(Exception):
    """Base exception for all DPR application errors."""

    def __init__(self, message: str = "An unexpected error occurred") -> None:
        self.message = message
        super().__init__(self.message)


class DatabaseError(DPRBaseError):
    """Raised when a database operation fails."""


class ExternalAPIError(DPRBaseError):
    """Raised when an external API call (Gemini, HuggingFace) fails."""


class AnalysisError(DPRBaseError):
    """Raised when content analysis fails."""


class CollectionError(DPRBaseError):
    """Raised when data collection fails."""


class NotFoundError(HTTPException):
    """HTTP 404 — resource not found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ValidationError(HTTPException):
    """HTTP 422 — validation error."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
