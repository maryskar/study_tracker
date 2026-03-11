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
def integration_db(tmp_path, monkeypatch):
    db_file = Path(tmp_path) / "integration_study.db"
    real_connect = sqlite3.connect

    def _connect(_path, **kwargs):
        return real_connect(db_file, **kwargs)

    monkeypatch.setattr(database_module.sqlite3, "connect", _connect)
    db = Database()
    yield db
    db.conn.close()


@pytest.fixture
def integration_auth(integration_db):
    return AuthManager(integration_db)


@pytest.fixture
def integration_timer(integration_db, monkeypatch):
    import program_files.timer as timer_module

    monkeypatch.setattr(timer_module, "BackgroundScheduler", InlineScheduler)
    return TimerManager(integration_db, lambda: None)

