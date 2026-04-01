from datetime import datetime
from unittest.mock import patch

import pytest
import requests
from jose import jwt

from program_files.api_client import MotivationAPI, ScheduleAPI, WorldTimeAPI


@pytest.mark.e2e
def test_e2e_01_register_login_complete_pomodoro_flow(e2e_auth, e2e_timer, e2e_db, complete_pomodoro):
    assert e2e_auth.register("e2e_user_01", "pass01") is True
    user = e2e_auth.login("e2e_user_01", "pass01")

    e2e_timer.start_session(user["id"], "pomodoro", lambda _value: None)
    complete_pomodoro()

    sessions = e2e_db.get_user_sessions(user["id"])
    achievements = e2e_db.get_achievements(user["id"])

    assert len(sessions) == 1
    assert sessions[0][5] == "pomodoro"
    assert sessions[0][3] is not None
    assert len(achievements) == 1


@pytest.mark.e2e
def test_e2e_02_stopwatch_then_pomodoro_flow(e2e_auth, e2e_timer, e2e_db, complete_pomodoro):
    assert e2e_auth.register("e2e_user_02", "pass02") is True
    user = e2e_auth.login("e2e_user_02", "pass02")

    e2e_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    e2e_timer.stop_timer()

    e2e_timer.start_session(user["id"], "pomodoro", lambda _value: None)
    complete_pomodoro()

    sessions = e2e_db.get_user_sessions(user["id"])
    session_types = [session[5] for session in sessions]

    assert len(sessions) == 2
    assert "stopwatch" in session_types
    assert "pomodoro" in session_types


@pytest.mark.e2e
def test_e2e_03_duplicate_registration_then_existing_login(e2e_auth, e2e_timer, e2e_db):
    assert e2e_auth.register("e2e_user_03", "pass03") is True
    assert e2e_auth.register("e2e_user_03", "newpass03") is False

    user = e2e_auth.login("e2e_user_03", "pass03")
    e2e_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    e2e_timer.stop_timer()

    sessions = e2e_db.get_user_sessions(user["id"])
    assert len(sessions) == 1


@pytest.mark.e2e
def test_e2e_04_failed_login_then_successful_login(e2e_auth, e2e_timer, e2e_db):
    assert e2e_auth.register("e2e_user_04", "pass04") is True
    assert e2e_auth.login("e2e_user_04", "wrong04") is False

    user = e2e_auth.login("e2e_user_04", "pass04")
    e2e_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    e2e_timer.stop_timer()

    sessions = e2e_db.get_user_sessions(user["id"])
    assert len(sessions) == 1


@pytest.mark.e2e
@patch("program_files.api_client.requests.get")
def test_e2e_05_happy_path_external_services(mock_get, e2e_auth, e2e_timer, e2e_db):
    def _side_effect(url, **kwargs):
        class Resp:
            def raise_for_status(self):
                return None

            def json(self_inner):
                if "quotable" in url:
                    return {"content": "Study hard."}
                if "worldtimeapi" in url:
                    return {"datetime": "2026-04-01T12:30:00+03:00"}
                if "/groups/" in url:
                    return {"name": "5130904/20104", "faculty": {"name": "ИКНТ"}, "course": 3}
                return {
                    "week": {"date_start": "2026-03-30", "date_end": "2026-04-05", "is_odd": False},
                    "days": [],
                }

        return Resp()

    mock_get.side_effect = _side_effect

    quote = MotivationAPI.get_quote()
    current_time = WorldTimeAPI.get_formatted_time()
    group = ScheduleAPI.get_group_info(40520)
    schedule = ScheduleAPI.get_group_schedule(40520, "2026-04-01")

    assert quote == "Study hard."
    assert current_time.startswith("2026-04-01")
    assert group["name"] == "5130904/20104"
    assert "week" in schedule

    assert e2e_auth.register("e2e_user_05", "pass05") is True
    user = e2e_auth.login("e2e_user_05", "pass05")
    e2e_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    e2e_timer.stop_timer()
    assert len(e2e_db.get_user_sessions(user["id"])) == 1


@pytest.mark.e2e
@patch("program_files.api_client.requests.get", side_effect=requests.exceptions.Timeout("timeout"))
def test_e2e_06_fallback_path_external_services(_mock_get):
    quote = MotivationAPI.get_quote()
    current_time = WorldTimeAPI.get_formatted_time()
    group = ScheduleAPI.get_group_info(40520)
    schedule = ScheduleAPI.get_group_schedule(40520)

    assert isinstance(quote, str) and quote != ""
    assert isinstance(current_time, str) and len(current_time) == 19
    assert group["name"] == "5130904/20104"
    assert "days" in schedule


@pytest.mark.e2e
def test_e2e_07_two_users_data_isolation(e2e_auth, e2e_timer, e2e_db, complete_pomodoro):
    assert e2e_auth.register("e2e_user_07_a", "pass") is True
    assert e2e_auth.register("e2e_user_07_b", "pass") is True

    user_a = e2e_auth.login("e2e_user_07_a", "pass")
    user_b = e2e_auth.login("e2e_user_07_b", "pass")

    e2e_timer.start_session(user_a["id"], "pomodoro", lambda _value: None)
    complete_pomodoro()

    e2e_timer.start_session(user_b["id"], "stopwatch", lambda _value: None)
    e2e_timer.stop_timer()

    sessions_a = e2e_db.get_user_sessions(user_a["id"])
    sessions_b = e2e_db.get_user_sessions(user_b["id"])

    assert len(sessions_a) == 1
    assert len(sessions_b) == 1
    assert sessions_a[0][5] == "pomodoro"
    assert sessions_b[0][5] == "stopwatch"


@pytest.mark.e2e
def test_e2e_08_monthly_report_generation_flow(e2e_auth, e2e_db):
    assert e2e_auth.register("e2e_user_08", "pass08") is True
    user = e2e_auth.login("e2e_user_08", "pass08")

    e2e_db.create_session(user["id"], "2026-03-01 10:00:00", "pomodoro")
    e2e_db.create_session(user["id"], "2026-03-10 10:00:00", "stopwatch")
    e2e_db.create_session(user["id"], "2026-04-01 10:00:00", "pomodoro")

    march = e2e_db.get_month_sessions(user["id"], 3, 2026)
    april = e2e_db.get_month_sessions(user["id"], 4, 2026)

    assert len(march) == 2
    assert len(april) == 1


@pytest.mark.e2e
def test_e2e_09_safe_stop_without_active_session(e2e_auth, e2e_timer, e2e_db):
    assert e2e_auth.register("e2e_user_09", "pass09") is True
    user = e2e_auth.login("e2e_user_09", "pass09")

    e2e_timer.stop_timer()

    sessions = e2e_db.get_user_sessions(user["id"])
    assert sessions == []


@pytest.mark.e2e
def test_e2e_10_auth_token_and_session_link(e2e_auth, e2e_timer, e2e_db):
    assert e2e_auth.register("e2e_user_10", "pass10") is True
    user = e2e_auth.login("e2e_user_10", "pass10")

    payload = jwt.decode(
        user["token"],
        e2e_auth.SECRET_KEY,
        algorithms=[e2e_auth.ALGORITHM],
    )

    assert payload["sub"] == str(user["id"])

    e2e_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    e2e_timer.stop_timer()

    sessions = e2e_db.get_user_sessions(user["id"])
    assert len(sessions) == 1
    assert sessions[0][1] == user["id"]
    assert datetime.strptime(sessions[0][2], "%Y-%m-%d %H:%M:%S")
