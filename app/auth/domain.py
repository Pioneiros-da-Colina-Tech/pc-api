from dataclasses import dataclass

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


@dataclass
class AuthenticationUseCase:
    pwd_context: CryptContext = CryptContext(
        schemes=["bcrypt"], deprecated="auto"
    )
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    def _verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)

    def _get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    def _get_user(self, username: str):
        return {"username": username, "password": "admin"}

    def _authenticate_user(self, username: str, password: str):
        user = self._get_user(username)
        if not user:
            return False
        if not self._verify_password(password, user.hashed_password):
            return False
        return user
