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
    assert auth.register("test_user", "test_pass")
    
    user = auth.login("test_user", "test_pass")
    assert user 

    timer.start_session(user["id"], "pomodoro", lambda x: None)
    sessions = db.get_user_sessions(user["id"])
    assert len(sessions) == 1

    timer.stop_timer()
    session = db.get_user_sessions(user["id"])[0]
    assert session[3] 
    assert session[4]