import sqlite3
from pathlib import Path

import pytest

from program_files.auth import AuthManager
from program_files.database import Database
import program_files.database as database_module
from program_files.timer import TimerManager


class InlineScheduler:
    def __init__(self):
        self.jobs = []

    def start(self):
        return None

    def add_job(self, func, trigger, seconds, args):
        self.jobs.append((func, trigger, seconds, args))

    def remove_all_jobs(self):
        self.jobs.clear()


@pytest.fixture
def system_db(tmp_path, monkeypatch):
    db_file = Path(tmp_path) / "system_study.db"
    real_connect = sqlite3.connect

    def _connect(_path, **kwargs):
        return real_connect(db_file, **kwargs)

    monkeypatch.setattr(database_module.sqlite3, "connect", _connect)
    db = Database()
    yield db
    db.conn.close()


@pytest.fixture
def system_auth(system_db):
    return AuthManager(system_db)


@pytest.fixture
def system_timer(system_db, monkeypatch):
    import program_files.timer as timer_module

    monkeypatch.setattr(timer_module, "BackgroundScheduler", InlineScheduler)
    return TimerManager(system_db, lambda: None)
