from collections.abc import Collection
from http import HTTPStatus
from typing import final

from pydantic import BaseModel


class FieldError(BaseModel):
    """
    Represents a specific error related to a field in a request payload.

    Attributes:
        name (str): The name of the field that has an error.
        detail (str): A detailed description of the error for the field.
    """

    name: str
    detail: str


@final
class APIError(Exception):
    """
    Custom exception class for representing API errors with detailed information.

    This class extends Python's built-in Exception and adds fields to provide
    more context about the error, such as HTTP status code, a user-friendly
    message, and specific field-level errors.
    """

    def __init__(
        self,
        message: str,
        detail: str | None = None,
        status_code: int = HTTPStatus.BAD_REQUEST,
        fields: list[FieldError] | None = None,
    ):
        """
        Initializes an APIError instance.

        Args:
            message (str): A concise, user-friendly message describing the error.
            detail (str | None, optional): A more detailed explanation of the error. Defaults to None.
            status_code (int, optional): The HTTP status code associated with the error.
                                         Defaults to HTTPStatus.BAD_REQUEST.
            fields (list[FieldError] | None, optional): A list of FieldError objects
                                                        for validation errors. Defaults to None.
        """
        super().__init__(message)
        self.message = message
        self.detail = detail
        self.status_code = status_code
        self.fields = fields or []

    def to_dict(self) -> dict:
        """
        Converts the APIError instance into a dictionary representation.

        Returns:
            dict: A dictionary containing the error's message, detail,
                  field errors (if any), and status code.
        """
        return {
            "message": self.message,
            "detail": self.detail,
            "fields": list(map(lambda field: field.model_dump(), self.fields)),
            "status_code": self.status_code,
        }


def environment_not_set(key: str) -> APIError:
    """
    Creates an APIError for when a required environment variable is not set.

    Args:
        key (str): The name of the environment variable that is missing.

    Returns:
        APIError: An APIError instance with status code 500 (INTERNAL_SERVER_ERROR).
    """
    return APIError(
        message="Environment variable not set",
        detail=f"The env key {key} is unset",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def does_not_exist(obj: str = "Object") -> APIError:
    """
    Creates an APIError for a resource that does not exist.

    Args:
        obj (str, optional): A description of the object that was not found.
                             Defaults to "Object".

    Returns:
        APIError: An APIError instance with status code 404 (NOT_FOUND).
    """
    return APIError(
        message=f"{obj} not found",
        status_code=HTTPStatus.NOT_FOUND,
    )


def already_exists(
    obj: str = "Object", fields: Collection[FieldError] = ()
) -> APIError:
    """
    Creates an APIError for a resource that already exists.

    Args:
        obj (str, optional): A description of the object that already exists.
                             Defaults to "Object".
        fields (Collection[FieldError], optional): A collection of field errors
                                                   indicating which fields caused the conflict.
                                                   Defaults to an empty tuple.

    Returns:
        APIError: An APIError instance with status code 409 (CONFLICT).
    """
    return APIError(
        message=f"{obj} already exists",
        status_code=HTTPStatus.CONFLICT,
        fields=list(fields),
    )


def unexpected_error(detail: str | None = None) -> APIError:
    """
    Creates a generic APIError for an unexpected server-side error.

    Args:
        detail (str | None, optional): A more detailed explanation of the unexpected error.
                                       Defaults to None.

    Returns:
        APIError: An APIError instance with status code 500 (INTERNAL_SERVER_ERROR).
    """
    return APIError(
        message="An unexpected error occurred, talk to the tech team",
        detail=detail,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def unauthenticated() -> APIError:
    """
    Creates an APIError for an unauthenticated request.

    This error is used when a request lacks valid authentication credentials.

    Returns:
        APIError: An APIError instance with status code 401 (UNAUTHORIZED).
    """
    return APIError(
        message="You are not authenticated",
        status_code=HTTPStatus.UNAUTHORIZED,
    )


def unauthorized_error() -> APIError:
    """
    Creates an APIError for an unauthorized request.

    This error is used when a user is authenticated but does not have the
    necessary permissions to access a resource or perform an action.

    Returns:
        APIError: An APIError instance with status code 403 (FORBIDDEN).
    """
    return APIError(
        message="You do not have permission to use this route",
        status_code=HTTPStatus.FORBIDDEN,
    )


def inactive_user() -> APIError:
    """
    Creates an APIError for an inactive user.

    This error is used when a user is disabled and cannot perform actions.

    Returns:
        APIError: An APIError instance with status code 400 (BAD_REQUEST).
    """
    return APIError(
        message="Inactive user",
        status_code=HTTPStatus.FORBIDDEN,
    )


def invalid_or_expired_token() -> APIError:
    """
    Creates an APIError for an invalid or expired authentication token.

    This is a specific type of authentication error.

    Returns:
        APIError: An APIError instance with status code 401 (UNAUTHORIZED).
    """
    return APIError(
        message="Token is invalid or expired",
        status_code=HTTPStatus.UNAUTHORIZED,
    )


def validation_error(
    message: str = "Validation error",
    fields: list[FieldError] | None = None,
    detail: str | None = None,
) -> APIError:
    """
    Creates an APIError for validation failures in request data.

    Args:
        message (str, optional): A general message about the validation error.
                                 Defaults to "Validation error".
        fields (list[FieldError] | None, optional): A list of specific field errors.
                                                    Defaults to None.
        detail (str | None, optional): A more detailed explanation of the validation error.
                                       Defaults to None.

    Returns:
        APIError: An APIError instance with status code 400 (BAD_REQUEST).
    """
    return APIError(
        message=message,
        detail=detail,
        status_code=HTTPStatus.BAD_REQUEST,
        fields=fields,
    )
