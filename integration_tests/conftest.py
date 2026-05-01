import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import program_files.database as database_module
from program_files.auth import AuthManager
from program_files.database import Database
from program_files.timer import TimerManager


class InlineScheduler:
    def __init__(self):
        self.jobs = []
        self.started = False

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


@pytest.fixture
def register_and_login(integration_auth):
    def _register_and_login(username="integration_user", password="pass"):
        assert integration_auth.register(username, password) is True
        user = integration_auth.login(username, password)
        assert user
        return user

    return _register_and_login


@pytest.fixture
def complete_current_pomodoro(integration_timer):
    def _complete(update_ui=None):
        if update_ui is None:
            update_ui = lambda _value: None

        integration_timer.start_time = datetime.now() - timedelta(seconds=1500)
        integration_timer._update_timer(update_ui)

    return _complete
