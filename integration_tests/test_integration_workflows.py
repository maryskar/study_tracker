from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
import requests

from program_files.api_client import MotivationAPI, ScheduleAPI, WorldTimeAPI


@pytest.mark.integration
def test_scenario_01_register_login_start_stop_pomodoro(integration_auth, integration_timer, integration_db):
    assert integration_auth.register("int_user_1", "pass_1") is True
    user = integration_auth.login("int_user_1", "pass_1")

    integration_timer.start_session(user["id"], "pomodoro", lambda _value: None)
    integration_timer.stop_timer()

    sessions = integration_db.get_user_sessions(user["id"])
    assert len(sessions) == 1
    assert sessions[0][5] == "pomodoro"


@pytest.mark.integration
def test_scenario_02_duplicate_registration_negative(integration_auth):
    assert integration_auth.register("int_user_2", "pass") is True
    assert integration_auth.register("int_user_2", "pass_new") is False


@pytest.mark.integration
def test_scenario_03_login_wrong_password_negative(integration_auth):
    integration_auth.register("int_user_3", "correct")
    assert integration_auth.login("int_user_3", "wrong") is False


@pytest.mark.integration
def test_scenario_04_stopwatch_session_persisted(integration_auth, integration_timer, integration_db):
    integration_auth.register("int_user_4", "pass")
    user = integration_auth.login("int_user_4", "pass")

    integration_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    integration_timer.stop_timer()

    sessions = integration_db.get_user_sessions(user["id"])
    assert len(sessions) == 1
    assert sessions[0][5] == "stopwatch"


@pytest.mark.integration
def test_scenario_05_pomodoro_completion_adds_achievement(integration_auth, integration_timer, integration_db):
    integration_auth.register("int_user_5", "pass")
    user = integration_auth.login("int_user_5", "pass")

    integration_timer.start_session(user["id"], "pomodoro", lambda _value: None)
    integration_timer.start_time = datetime.now() - timedelta(seconds=1500)
    integration_timer._update_timer(lambda _value: None)

    achievements = integration_db.get_achievements(user["id"])
    assert len(achievements) == 1


@pytest.mark.integration
@patch("program_files.api_client.requests.get")
def test_scenario_06_external_services_happy_path(mock_get, integration_auth, integration_timer):
    def _side_effect(url, **kwargs):
        class Resp:
            def raise_for_status(self):
                return None

            def json(self_inner):
                if "quotable" in url:
                    return {"content": "Work now, rest later."}
                if "worldtimeapi" in url:
                    return {"datetime": "2026-03-11T12:00:00+03:00"}
                return {
                    "week": {"date_start": "2026-03-10", "date_end": "2026-03-16", "is_odd": False},
                    "days": [],
                }

        return Resp()

    mock_get.side_effect = _side_effect

    assert isinstance(MotivationAPI.get_quote(), str)
    assert isinstance(WorldTimeAPI.get_formatted_time(), str)
    schedule = ScheduleAPI.get_group_schedule(40520, "2026-03-11")
    assert "week" in schedule

    integration_auth.register("int_user_6", "pass")
    user = integration_auth.login("int_user_6", "pass")
    integration_timer.start_session(user["id"], "pomodoro", lambda _value: None)
    integration_timer.stop_timer()


@pytest.mark.integration
@patch("program_files.api_client.requests.get", side_effect=requests.exceptions.Timeout("timeout"))
def test_scenario_07_external_services_fallback_negative(_mock_get):
    quote = MotivationAPI.get_quote()
    current = WorldTimeAPI.get_formatted_time()
    schedule = ScheduleAPI.get_group_schedule(40520)

    assert isinstance(quote, str)
    assert isinstance(current, str)
    assert "days" in schedule


@pytest.mark.integration
def test_scenario_08_month_filter_by_user(integration_auth, integration_db):
    integration_auth.register("int_user_8a", "pass")
    integration_auth.register("int_user_8b", "pass")
    user_a = integration_auth.login("int_user_8a", "pass")
    user_b = integration_auth.login("int_user_8b", "pass")

    integration_db.create_session(user_a["id"], "2026-03-01 10:00:00", "pomodoro")
    integration_db.create_session(user_b["id"], "2026-03-01 10:00:00", "pomodoro")

    only_a = integration_db.get_month_sessions(user_a["id"], 3, 2026)
    assert len(only_a) == 1


@pytest.mark.integration
def test_scenario_09_two_sessions_in_sequence(integration_auth, integration_timer, integration_db):
    integration_auth.register("int_user_9", "pass")
    user = integration_auth.login("int_user_9", "pass")

    integration_timer.start_session(user["id"], "pomodoro", lambda _value: None)
    integration_timer.stop_timer()

    integration_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    integration_timer.stop_timer()

    sessions = integration_db.get_user_sessions(user["id"])
    assert len(sessions) == 2


@pytest.mark.integration
def test_scenario_10_stop_without_start_negative(integration_timer, integration_auth, integration_db):
    integration_auth.register("int_user_10", "pass")
    user = integration_auth.login("int_user_10", "pass")

    integration_timer.stop_timer()
    sessions = integration_db.get_user_sessions(user["id"])
    assert sessions == []

