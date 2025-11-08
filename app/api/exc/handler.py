from fastapi import Request, Response
from fastapi.responses import ORJSONResponse

from .exceptions import APIError


async def api_error_handler(_: Request, exc: APIError) -> Response:
    return ORJSONResponse(
        exc.to_dict(), status_code=exc.status_code, headers={"X-Error": exc.message}
    )
