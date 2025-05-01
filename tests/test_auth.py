import unittest
from database import Database
from auth import AuthManager
from jose import jwt
import datetime

class TestAuthManager(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.db.conn.execute("DELETE FROM users")
        self.db.conn.commit()
        self.auth = AuthManager(self.db)