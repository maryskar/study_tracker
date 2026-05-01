from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
import requests
from jose import jwt

from program_files.api_client import MotivationAPI, ScheduleAPI, WorldTimeAPI

GROUP_ID = 40520


class FakeResponse:
    def __init__(self, payload, status_error=None):
        self.payload = payload
        self.status_error = status_error

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error


@pytest.mark.integration
def test_scenario_01_registration_login_token_and_pomodoro_session(
    integration_auth,
    integration_timer,
    integration_db,
    register_and_login,
):
    user = register_and_login("int_user_01", "pass_01")
    payload = jwt.decode(
        user["token"],
        integration_auth.SECRET_KEY,
        algorithms=[integration_auth.ALGORITHM],
    )

    integration_timer.start_session(user["id"], "pomodoro", lambda _value: None)
    integration_timer.stop_timer()

    sessions = integration_db.get_user_sessions(user["id"])
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    assert payload["sub"] == str(user["id"])
    assert expires_at > datetime.now(timezone.utc)
    assert len(sessions) == 1
    assert sessions[0][1] == user["id"]
    assert sessions[0][5] == "pomodoro"
    assert sessions[0][3] is not None


@pytest.mark.integration
def test_scenario_02_duplicate_registration_keeps_original_account(
    integration_auth,
    integration_timer,
    integration_db,
):
    assert integration_auth.register("int_user_02", "original") is True
    assert integration_auth.register("int_user_02", "replacement") is False

    assert integration_auth.login("int_user_02", "replacement") is False
    user = integration_auth.login("int_user_02", "original")

    integration_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    integration_timer.stop_timer()

    users_count = integration_db.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    sessions = integration_db.get_user_sessions(user["id"])

    assert users_count == 1
    assert len(sessions) == 1


@pytest.mark.integration
def test_scenario_03_failed_login_does_not_create_session(integration_auth, integration_db):
    assert integration_auth.register("int_user_03", "correct") is True

    failed_user = integration_auth.login("int_user_03", "wrong")
    sessions_count = integration_db.conn.execute("SELECT COUNT(*) FROM study_sessions").fetchone()[0]

    assert failed_user is False
    assert sessions_count == 0


@pytest.mark.integration
def test_scenario_04_completed_pomodoro_records_session_and_achievement(
    integration_timer,
    integration_db,
    register_and_login,
    complete_current_pomodoro,
):
    user = register_and_login("int_user_04", "pass_04")
    updated_labels = []

    integration_timer.start_session(user["id"], "pomodoro", updated_labels.append)
    complete_current_pomodoro(updated_labels.append)

    sessions = integration_db.get_user_sessions(user["id"])
    achievements = integration_db.get_achievements(user["id"])

    assert integration_timer.running is False
    assert integration_timer.scheduler.jobs == []
    assert len(sessions) == 1
    assert sessions[0][4] >= 1500
    assert len(achievements) == 1


@pytest.mark.integration
def test_scenario_05_stopwatch_updates_ui_and_persists_duration(
    integration_timer,
    integration_db,
    register_and_login,
):
    user = register_and_login("int_user_05", "pass_05")
    rendered = []

    integration_timer.start_session(user["id"], "stopwatch", rendered.append)
    integration_timer.start_time = datetime.now() - timedelta(seconds=3)
    integration_timer._update_stopwatch(rendered.append)
    integration_timer.stop_timer()

    sessions = integration_db.get_user_sessions(user["id"])

    assert rendered
    assert ":" in rendered[-1]
    assert len(sessions) == 1
    assert sessions[0][4] >= 3
    assert sessions[0][5] == "stopwatch"


# Вспомогательный mock-ответ для requests.get
 
def _make_mock_response(url, **kwargs):
 
    class _Response:
        def raise_for_status(self):
            pass
 
        def json(self_inner):
            if "quotable" in url:
                return {"content": "Work now, rest later."}
            if "worldtimeapi" in url:
                return {"datetime": "2026-03-11T12:00:00+03:00"}
            if "groups" in url:
                return {
                    "name": "5130904/20104",
                    "faculty": {"name": "Институт компьютерных наук и кибербезопасности"},
                    "course": 3,
                }
            return {
                "week": {
                    "date_start": "2026-03-10",
                    "date_end": "2026-03-16",
                    "is_odd": False,
                },
                "days": [
                    {
                        "weekday": 1,
                        "date": "2026-03-10",
                        "lessons": [
                            {
                                "time_start": "09:00",
                                "time_end": "10:30",
                                "subject": "Тестирование ПО",
                                "typeObj": {"abbr": "Лек"},
                                "auditories": [{"building": {"name": "Главный"}, "name": "101"}],
                                "teachers": [{"full_name": "Иванов И.И."}],
                                "lms_url": "https://lms.spbstu.ru/course/1",
                            }
                        ],
                    }
                ],
            }
 
    return _Response()


@pytest.mark.integration
@patch("program_files.api_client.requests.get", side_effect=_make_mock_response)
def test_scenario_06_external_services_happy_path(_mock_get):
    # Блок 1: MotivationAPI возвращает непустую строку-цитату
    quote = MotivationAPI.get_quote()
    assert isinstance(quote, str)
    assert quote == "Work now, rest later."

    # Блок 2: WorldTimeAPI возвращает время в формате YYYY-MM-DD HH:MM:SS
    current_time = WorldTimeAPI.get_formatted_time()
    assert len(current_time) == 19
    datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")

    # Блок 3: ScheduleAPI.get_group_info возвращает корректную структуру группы
    group_info = ScheduleAPI.get_group_info(GROUP_ID)
    assert group_info["name"] == "5130904/20104"

    # Блок 4: ScheduleAPI.get_group_schedule возвращает расписание с неделей и днями
    schedule = ScheduleAPI.get_group_schedule(GROUP_ID, date="2026-03-10")

    assert "week" in schedule
    assert "days" in schedule

    lesson = schedule["days"][0]["lessons"][0]

    assert lesson["subject"] == "Тестирование ПО"
    assert lesson["room"] == "Главный 101"
    assert lesson["teacher"] == "Иванов И.И."


@pytest.mark.integration
@pytest.mark.parametrize(
    "error_cls",
    [
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ],
)
@patch("program_files.api_client.requests.get")
def test_scenario_07_each_api_fallback_independently(mock_get, error_cls):
    mock_get.side_effect = error_cls("simulated error")
 
    # MotivationAPI
    quote = MotivationAPI.get_quote()
    assert isinstance(quote, str) and len(quote) > 0
 
    # WorldTimeAPI
    t = WorldTimeAPI.get_formatted_time()
    assert len(t) == 19
    datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
 
    # ScheduleAPI - schedule
    schedule = ScheduleAPI.get_group_schedule(GROUP_ID)
    assert "week" in schedule and "days" in schedule
 
    # ScheduleAPI - group_info
    info = ScheduleAPI.get_group_info(GROUP_ID)
    assert info["name"] == "5130904/20104"


@pytest.mark.integration
def test_scenario_08_two_users_have_isolated_sessions_and_reports(
    integration_auth,
    integration_db,
):
    assert integration_auth.register("int_user_08_a", "pass") is True
    assert integration_auth.register("int_user_08_b", "pass") is True
    user_a = integration_auth.login("int_user_08_a", "pass")
    user_b = integration_auth.login("int_user_08_b", "pass")

    integration_db.create_session(user_a["id"], "2026-03-01 10:00:00", "pomodoro")
    integration_db.create_session(user_a["id"], "2026-03-15 11:00:00", "stopwatch")
    integration_db.create_session(user_b["id"], "2026-03-01 10:00:00", "pomodoro")
    integration_db.add_achievement(user_a["id"], "A", "Only user A")

    user_a_march = integration_db.get_month_sessions(user_a["id"], 3, 2026)
    user_b_march = integration_db.get_month_sessions(user_b["id"], 3, 2026)

    assert len(user_a_march) == 2
    assert len(user_b_march) == 1
    assert len(integration_db.get_achievements(user_a["id"])) == 1
    assert integration_db.get_achievements(user_b["id"]) == []


@pytest.mark.integration
def test_scenario_09_sequential_sessions_are_saved_and_scheduler_is_cleared(
    integration_timer,
    integration_db,
    register_and_login,
):
    user = register_and_login("int_user_09", "pass_09")

    integration_timer.start_session(user["id"], "pomodoro", lambda _value: None)
    assert integration_timer.scheduler.jobs[-1]["func"] == integration_timer._update_timer
    integration_timer.stop_timer()

    integration_timer.start_session(user["id"], "stopwatch", lambda _value: None)
    assert integration_timer.scheduler.jobs[-1]["func"] == integration_timer._update_stopwatch
    integration_timer.stop_timer()

    sessions = integration_db.get_user_sessions(user["id"])

    assert integration_timer.scheduler.jobs == []
    assert len(sessions) == 2
    assert {session[5] for session in sessions} == {"pomodoro", "stopwatch"}


@pytest.mark.integration
def test_scenario_10_stop_without_start_and_break_completion_are_safe(
    integration_timer,
    integration_db,
    register_and_login,
):
    user = register_and_login("int_user_10", "pass_10")

    integration_timer.stop_timer()
    assert integration_db.get_user_sessions(user["id"]) == []

    integration_timer.start_session(user["id"], "short_break", lambda _value: None)
    integration_timer.start_time = datetime.now() - timedelta(seconds=300)
    integration_timer._update_timer(lambda _value: None)

    sessions = integration_db.get_user_sessions(user["id"])
    achievements = integration_db.get_achievements(user["id"])

    assert len(sessions) == 1
    assert sessions[0][5] == "short_break"
    assert achievements == []
