# auth.py
from passlib.context import CryptContext
from jose import jwt
import datetime

class AuthManager:
    def __init__(self, db):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = "super_secret_key_123!"
        self.ALGORITHM = "HS256"
        
    def register(self, username, password):
        hashed = self.pwd_context.hash(password)
        return self.db.create_user(username, hashed)
        
    def login(self, username, password):
        if user := self.db.get_user(username):
            if self.pwd_context.verify(password, user[2]):
                return {
                    "id": user[0],
                    "username": user[1],
                    "token": self.create_access_token(user[0])
                }
        return False
    
    def create_access_token(self, user_id):
        expires = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
        return jwt.encode({
            "sub": str(user_id),
            "exp": expires
        }, self.SECRET_KEY, algorithm=self.ALGORITHM)