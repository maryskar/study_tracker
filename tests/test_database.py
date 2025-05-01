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

    def test_create_session_and_get(self):
        self.db.create_user("u1", "h")
        user_id = self.db.get_user("u1")[0]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sid = self.db.create_session(user_id, now, "pomodoro")
        self.assertIsInstance(sid, int)
        sessions = self.db.get_user_sessions(user_id)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0][0], sid)
        self.assertEqual(sessions[0][2], now)
        end = (datetime.now() + timedelta(minutes=25)).strftime("%Y-%m-%d %H:%M:%S") # обновляем сессию
        self.db.update_session(sid, end, 1500)
        updated = self.db.get_user_sessions(user_id)[0]
        self.assertEqual(updated[3], end)
        self.assertEqual(updated[4], 1500)