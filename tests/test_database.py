import unittest
from program_files.database import Database
from datetime import datetime, timedelta

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        for tbl in ("users", "study_sessions", "achievements"):
            self.db.conn.execute(f"DELETE FROM {tbl}")
        self.db.conn.commit()

    def test_create_and_get_user(self):
        ok = self.db.create_user("testuser", "hash")
        self.assertTrue(ok)
        user = self.db.get_user("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "testuser")