import sqlite3
from datetime import datetime, timedelta
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
def e2e_db(tmp_path, monkeypatch):
    db_file = Path(tmp_path) / "e2e_study.db"
    real_connect = sqlite3.connect

    def _connect(_path, **kwargs):
        return real_connect(db_file, **kwargs)

    monkeypatch.setattr(database_module.sqlite3, "connect", _connect)
    db = Database()
    yield db
    db.conn.close()


@pytest.fixture
def e2e_auth(e2e_db):
    return AuthManager(e2e_db)


@pytest.fixture
def e2e_timer(e2e_db, monkeypatch):
    import program_files.timer as timer_module

    monkeypatch.setattr(timer_module, "BackgroundScheduler", InlineScheduler)
    return TimerManager(e2e_db, lambda: None)


@pytest.fixture
def complete_pomodoro(e2e_timer):
    def _complete(update_ui=None):
        if update_ui is None:
            update_ui = lambda _value: None

        e2e_timer.start_time = datetime.now() - timedelta(seconds=1500)
        e2e_timer._update_timer(update_ui)

    return _complete
