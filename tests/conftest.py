import sqlite3
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from program_files.auth import AuthManager
from program_files.database import Database
import program_files.database as database_module
import program_files.timer as timer_module
from program_files.timer import TimerManager


class FakeScheduler:
    def __init__(self):
        self.started = False
        self.jobs = []
        self.remove_all_jobs_calls = 0

    def start(self):
        self.started = True

    def add_job(self, func, trigger, seconds, args):
        self.jobs.append(
            {
                "func": func,
                "trigger": trigger,
                "seconds": seconds,
                "args": args,
            }
        )

    def remove_all_jobs(self):
        self.remove_all_jobs_calls += 1
        self.jobs.clear()


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    db_file = Path(tmp_path) / "study.db"
    real_connect = sqlite3.connect

    def _connect(_path, **kwargs):
        return real_connect(db_file, **kwargs)

    monkeypatch.setattr(database_module.sqlite3, "connect", _connect)
    db = Database()
    yield db
    db.conn.close()


@pytest.fixture
def auth_manager(isolated_db):
    return AuthManager(isolated_db)


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.create_session.return_value = 101
    return db


@pytest.fixture
def timer_manager(mock_db, monkeypatch):
    monkeypatch.setattr(timer_module, "BackgroundScheduler", FakeScheduler)
    return TimerManager(mock_db, MagicMock())

