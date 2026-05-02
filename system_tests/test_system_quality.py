from time import perf_counter
from unittest.mock import patch

import pytest
import requests

from program_files.api_client import ScheduleAPI, WorldTimeAPI


@pytest.mark.system
@pytest.mark.load
def test_load_001_mass_session_creation(system_auth, system_timer, system_db):
    assert system_auth.register("load_user", "pass") is True
    user = system_auth.login("load_user", "pass")

    start = perf_counter()
    for _ in range(180):
        system_timer.start_session(user["id"], "stopwatch", lambda _value: None)
        system_timer.stop_timer()

    elapsed = perf_counter() - start
    total_sessions = system_db.conn.execute("SELECT COUNT(*) FROM study_sessions").fetchone()[0]

    assert total_sessions == 180
    assert elapsed < 12


@pytest.mark.system
@pytest.mark.stability
def test_stability_001_repeated_start_stop_cycles(system_auth, system_timer, system_db):
    assert system_auth.register("stable_user", "pass") is True
    user = system_auth.login("stable_user", "pass")

    start = perf_counter()
    for _ in range(140):
        system_timer.start_session(user["id"], "stopwatch", lambda _value: None)
        system_timer.stop_timer()

    elapsed = perf_counter() - start
    total_sessions = system_db.conn.execute("SELECT COUNT(*) FROM study_sessions").fetchone()[0]

    assert total_sessions == 140
    assert system_timer.running is False
    assert len(system_timer.scheduler.jobs) == 0
    assert elapsed < 15


@pytest.mark.system
@pytest.mark.recovery
def test_recovery_001_api_fallback_then_normal_response(system_auth, system_timer, system_db):
    def side_effect(*args, **kwargs):
        if side_effect.calls == 0:
            side_effect.calls += 1
            raise requests.exceptions.Timeout("temporary failure")
        side_effect.calls += 1

        class Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return {"datetime": "2026-04-01T10:20:30+03:00"}

        return Resp()

    side_effect.calls = 0

    with patch("program_files.api_client.requests.get", side_effect=side_effect):
        fallback_time = WorldTimeAPI.get_formatted_time()
        recovered_time = WorldTimeAPI.get_formatted_time()

    assert len(fallback_time) == 19
    assert recovered_time == "2026-04-01 10:20:30"

    assert system_auth.register("recovery_user", "pass") is True
    user = system_auth.login("recovery_user", "pass")
    system_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    system_timer.stop_timer()

    sessions = system_db.get_user_sessions(user["id"])
    assert len(sessions) == 1


@pytest.mark.system
@pytest.mark.volume
def test_volume_001_large_dataset_month_query(system_auth, system_db):
    assert system_auth.register("volume_user", "pass") is True
    user = system_auth.login("volume_user", "pass")

    start_insert = perf_counter()
    for i in range(1200):
        month = 3 if i % 2 == 0 else 4
        day = (i % 28) + 1
        time_str = f"2026-{month:02d}-{day:02d} 10:00:00"
        system_db.create_session(user["id"], time_str, "pomodoro")

    insert_elapsed = perf_counter() - start_insert

    start_query = perf_counter()
    march_sessions = system_db.get_month_sessions(user["id"], 3, 2026)
    april_sessions = system_db.get_month_sessions(user["id"], 4, 2026)
    query_elapsed = perf_counter() - start_query

    assert len(march_sessions) == 600
    assert len(april_sessions) == 600
    assert insert_elapsed < 12
    assert query_elapsed < 3


@pytest.mark.system
@pytest.mark.recovery
def test_recovery_002_wrong_password_after_successful_registration(system_auth, system_timer, system_db):
    assert system_auth.register("recover_auth_user", "correct") is True
    assert system_auth.login("recover_auth_user", "wrong") is False

    user = system_auth.login("recover_auth_user", "correct")
    system_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    system_timer.stop_timer()

    assert len(system_db.get_user_sessions(user["id"])) == 1


@pytest.mark.system
@pytest.mark.recovery
def test_recovery_003_schedule_api_failure_does_not_break_system_flow(system_auth, system_timer, system_db):
    with patch("program_files.api_client.requests.get", side_effect=requests.exceptions.ConnectionError("offline")):
        schedule = ScheduleAPI.get_group_schedule(40520)

    assert "days" in schedule
    assert len(schedule["days"]) >= 1

    assert system_auth.register("recovery_user_2", "pass") is True
    user = system_auth.login("recovery_user_2", "pass")
    system_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    system_timer.stop_timer()

    assert len(system_db.get_user_sessions(user["id"])) == 1


@pytest.mark.system
@pytest.mark.stability
def test_stability_002_scheduler_queue_not_growing_unbounded(system_auth, system_timer):
    assert system_auth.register("queue_user", "pass") is True
    user = system_auth.login("queue_user", "pass")

    for _ in range(80):
        system_timer.start_session(user["id"], "pomodoro", lambda _value: None)
        assert len(system_timer.scheduler.jobs) <= 1
        system_timer.stop_timer()

    assert len(system_timer.scheduler.jobs) == 0


@pytest.mark.system
@pytest.mark.load
def test_load_002_multi_user_sequences(system_auth, system_timer, system_db):
    users = []
    for i in range(8):
        username = f"multi_user_{i}"
        assert system_auth.register(username, "pass") is True
        users.append(system_auth.login(username, "pass"))

    start = perf_counter()
    for user in users:
        for _ in range(10):
            system_timer.start_session(user["id"], "stopwatch", lambda _value: None)
            system_timer.stop_timer()
    elapsed = perf_counter() - start

    total_sessions = system_db.conn.execute("SELECT COUNT(*) FROM study_sessions").fetchone()[0]
    assert total_sessions == 80
    assert elapsed < 10


@pytest.mark.system
@pytest.mark.volume
def test_volume_002_large_achievement_set(system_auth, system_db):
    assert system_auth.register("ach_volume_user", "pass") is True
    user = system_auth.login("ach_volume_user", "pass")

    for i in range(400):
        system_db.add_achievement(user["id"], f"A{i}", f"D{i}")

    achievements = system_db.get_achievements(user["id"])
    assert len(achievements) == 400


@pytest.mark.system
@pytest.mark.recovery
def test_load_003_batch_token_generation(system_auth):
    tokens = []
    start = perf_counter()
    for i in range(300):
        token = system_auth.create_access_token(i + 1)
        tokens.append(token)
    elapsed = perf_counter() - start

    assert len(tokens) == 300
    assert all(isinstance(token, str) and token for token in tokens)
    assert elapsed < 5