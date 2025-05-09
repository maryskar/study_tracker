import time
import pytest
import sys

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
    
    assert auth.login("test_user", "test_pass")