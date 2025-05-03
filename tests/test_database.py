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
        end = (datetime.now() + timedelta(minutes=25)).strftime("%Y-%m-%d %H:%M:%S")
        self.db.update_session(sid, end, 1500)
        updated = self.db.get_user_sessions(user_id)[0]
        self.assertEqual(updated[3], end)
        self.assertEqual(updated[4], 1500)

    def test_month_sessions_filter(self):
        self.db.create_user("u2", "h")
        uid = self.db.get_user("u2")[0]
        now = datetime.now()
        march = now.replace(month=3, day=15).strftime("%Y-%m-%d %H:%M:%S")
        april = now.replace(month=4, day=10).strftime("%Y-%m-%d %H:%M:%S")
        self.db.create_session(uid, march, "stopwatch")
        self.db.create_session(uid, april, "pomodoro")
        march_list = self.db.get_month_sessions(uid, 3, now.year)
        april_list = self.db.get_month_sessions(uid, 4, now.year)
        self.assertEqual(len(march_list), 1)
        self.assertEqual(len(april_list), 1)

    def test_achievements(self):
        self.db.create_user("u3", "h")
        uid = self.db.get_user("u3")[0]
        self.db.add_achievement(uid, "First", "First achievement")
        achs = self.db.get_achievements(uid)
        self.assertEqual(len(achs), 1)
        self.assertEqual(achs[0][2], "First")
        self.assertEqual(achs[0][3], "First achievement")

    def test_create_user_duplicate(self):
        self.db.create_user("test", "hash")
        result = self.db.create_user("test", "another_hash")
        self.assertFalse(result)

    def tearDown(self):
       if hasattr(self, 'db') and self.db.conn:
           self.db.conn.close()