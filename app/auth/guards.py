from typing import Annotated

from fastapi import Depends

from app.api.exc import unauthorized_error as forbidden_error
from app.infra.database.adapter import SessionContext
from app.roles.concepts import Role
from app.roles.repository import UserRoleRepository

from .handler import AuthDependency, decode_token
from .repository import UserRepository

_ADMIN_ROLES = frozenset({Role.DIRETOR, Role.SECRETARIA, Role.TESOURARIA})
_ATTENDANCE_ROLES = frozenset(
    {Role.DIRETOR, Role.SECRETARIA, Role.CONSELHEIRO_UNIDADE}
)


def require_roles(*roles: Role):
    """
    FastAPI dependency factory.
    Raises HTTP 403 Forbidden if the authenticated user does not hold at least
    one of the given roles.
    """
    allowed = frozenset(roles)

    async def guard(
        credentials: AuthDependency, session: SessionContext
    ) -> None:
        token_data = await decode_token(credentials.credentials)
        user = await UserRepository(session).get(document=token_data.document)
        user_roles = await UserRoleRepository(session).get_roles_for_user(
            user.id_
        )
        if not frozenset(user_roles) & allowed:
            raise forbidden_error()

    return guard


AdminGuard = Annotated[None, Depends(require_roles(*_ADMIN_ROLES))]
AttendanceGuard = Annotated[None, Depends(require_roles(*_ATTENDANCE_ROLES))]
