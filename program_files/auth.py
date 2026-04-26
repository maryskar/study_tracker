# auth.py
import datetime

from jose import jwt
from passlib.context import CryptContext


class AuthManager:
    def __init__(self, db):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = "super_secret_key_123!"
        self.ALGORITHM = "HS256"

    @staticmethod
    def _is_valid_credential(value):
        return isinstance(value, str) and value.strip() != ""

    def register(self, username, password):
        if not self._is_valid_credential(username) or not self._is_valid_credential(password):
            return False

        try:
            hashed = self.pwd_context.hash(password)
        except Exception:
            return False

        return self.db.create_user(username, hashed)

    def login(self, username, password):
        if not self._is_valid_credential(username) or not self._is_valid_credential(password):
            return False

        if user := self.db.get_user(username):
            try:
                password_matches = self.pwd_context.verify(password, user[2])
            except Exception:
                return False

            if password_matches:
                return {
                    "id": user[0],
                    "username": user[1],
                    "token": self.create_access_token(user[0]),
                }
        return False

    def create_access_token(self, user_id):
        # timezone.utc works both on modern and older supported Python versions.
        expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        return jwt.encode(
            {
                "sub": str(user_id),
                "exp": expires,
            },
            self.SECRET_KEY,
            algorithm=self.ALGORITHM,
        )
