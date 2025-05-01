# database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('study.db', check_same_thread=False, timeout=10)
        self._init_db()
        
    def _init_db(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )''')
            
            self.conn.execute('''CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                duration INTEGER,
                type TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')
            
            self.conn.execute('''CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')

    def create_user(self, username, password_hash):
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username):
        cursor = self.conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        return cursor.fetchone()

    def create_session(self, user_id, start_time, session_type):
        cursor = self.conn.execute(
            "INSERT INTO study_sessions (user_id, start_time, type) VALUES (?, ?, ?)",
            (user_id, start_time, session_type)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def update_session(self, session_id, end_time, duration):
        self.conn.execute(
            "UPDATE study_sessions SET end_time = ?, duration = ? WHERE id = ?",
            (end_time, duration, session_id)
        )
        self.conn.commit()

    def get_user_sessions(self, user_id):
        cursor = self.conn.execute(
            "SELECT * FROM study_sessions WHERE user_id = ? ORDER BY start_time DESC",
            (user_id,)
        )
        return cursor.fetchall()

    def add_achievement(self, user_id, title, description):
        self.conn.execute(
            "INSERT INTO achievements (user_id, title, description) VALUES (?, ?, ?)",
            (user_id, title, description)
        )
        self.conn.commit()

    def get_month_sessions(self, user_id, month, year):
        cursor = self.conn.execute(
            """SELECT * FROM study_sessions 
            WHERE user_id = ? 
            AND strftime('%m', start_time) = ? 
            AND strftime('%Y', start_time) = ?""",
            (user_id, f"{month:02d}", str(year))
        )
        return cursor.fetchall()
    
    def get_achievements(self, user_id):
        cursor = self.conn.execute(
            "SELECT * FROM achievements WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchall()