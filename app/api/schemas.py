from pydantic import BaseModel


class BaseResponseSchema[T](BaseModel):
    """Base response schema for API responses."""

    status: int = 200
    message: str
    data: T
