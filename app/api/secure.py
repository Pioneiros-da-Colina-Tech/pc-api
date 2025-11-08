from collections.abc import Awaitable, Callable

import secure
from fastapi import Request, Response

secure_headers = secure.Secure.from_preset(secure.Preset.BASIC)


async def secure_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response = await call_next(request)
    secure_headers.set_headers(response)  # pyright: ignore[reportArgumentType]
    return response
