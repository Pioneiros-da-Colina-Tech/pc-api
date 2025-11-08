from typing import Any

from pydantic import BaseModel, Field

from app.api.exc.exceptions import APIError


class BaseResponseSchema[T](BaseModel):
    """Base response schema for API responses."""

    status: int = 200
    message: str
    data: T


class FieldErrorSchema(BaseModel):
    """Schema for field-level errors."""

    name: str = Field(..., description="The name of the field with the error")
    detail: str = Field(..., description="Details about the error")


class ErrorResponseSchema(BaseModel):
    """Schema for error responses."""

    message: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Additional error details")
    fields: list[FieldErrorSchema] = Field(
        default_factory=list, description="Field-level errors"
    )
    status_code: int = Field(..., description="HTTP status code")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "An unexpected error occurred, talk to the tech team",
                    "detail": None,
                    "fields": [],
                    "status_code": 500,
                }
            ]
        }
    }


def create_error_response(error: APIError) -> dict[str, Any]:
    """
    Create an OpenAPI error response structure for FastAPI route documentation.

    Args:
        error: An APIError instance to extract example data from

    Returns:
        A dictionary with the proper OpenAPI response format including
        description, model, and example content
    """
    status_descriptions = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        500: "Internal Server Error",
    }

    return {
        "description": status_descriptions.get(
            error.status_code, f"HTTP {error.status_code}"
        ),
        "model": ErrorResponseSchema,
        "content": {"application/json": {"example": error.to_dict()}},
    }
