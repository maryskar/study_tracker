import unittest
from database import Database
from auth import AuthManager
from jose import jwt
import datetime

class TestAuthManager(unittest.TestCase):
    def setUpUser(self):
        self.db = Database()
        self.db.conn.execute("DELETE FROM users")
        self.db.conn.commit()
        self.auth = AuthManager(self.db)

    def test_register_user_success(self):
        result = self.auth.register("alice", "password123")
        self.assertTrue(result)
        self.assertFalse(self.auth.register("alice", "anotherpass"))

    def test_login_success_and_token(self):
        self.auth.register("bob", "secret")
        login = self.auth.login("bob", "secret")
        self.assertIsInstance(login, dict)
        self.assertIn("token", login)
        payload = jwt.decode(  # Расшифруем токен и проверим sub
            login["token"],
            self.auth.SECRET_KEY,
            algorithms=[self.auth.ALGORITHM]
        )
        self.assertEqual(payload["sub"], str(login["id"]))
        exp = datetime.datetime.fromtimestamp(payload["exp"])  # exp в будущем
        self.assertGreater(exp, datetime.datetime.utcnow())