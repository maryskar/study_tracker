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