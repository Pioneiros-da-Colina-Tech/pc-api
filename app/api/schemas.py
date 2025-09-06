from pydantic import BaseModel, Field


class BaseResponseSchema[T](BaseModel):
    """Base response schema for API responses."""

    status: int = Field(..., ge=100, le=599, description="HTTP status code")
    message: str = Field(..., min_length=1, description="Message")
    data: T = Field(..., description="Response data")
