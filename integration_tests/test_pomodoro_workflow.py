import time
import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "program_files"))

from auth import AuthManager
from database import Database
from timer import TimerManager

@pytest.fixture
def db():
    return Database()

@pytest.fixture
def auth(db):
    return AuthManager(db)

@pytest.fixture
def timer(db):
    return TimerManager(db, lambda x: None)

def test_pomodoro_workflow(auth, timer, db):
    assert auth.register("test_user2", "test_pass")
    
    assert auth.login("test_user2", "test_pass")