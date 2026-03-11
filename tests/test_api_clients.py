from datetime import datetime
from unittest.mock import patch

import pytest
import requests

from program_files.api_client import MotivationAPI, ScheduleAPI, WorldTimeAPI


@pytest.mark.parametrize(
    "quote",
    [
        "Stay focused.",
        "Do one thing at a time.",
        "Small steps every day.",
        "Discipline beats mood.",
        "Consistency wins.",
    ],
)
@patch("program_files.api_client.requests.get")
def test_get_quote_success(mock_get, quote):
    mock_get.return_value.json.return_value = {"content": quote}
    assert MotivationAPI.get_quote() == quote


@pytest.mark.parametrize("error_cls", [Exception, RuntimeError, ValueError])
@patch("program_files.api_client.requests.get")
def test_get_quote_fallback_on_error(mock_get, error_cls):
    mock_get.side_effect = error_cls("network down")
    result = MotivationAPI.get_quote()
    assert isinstance(result, str)
    assert result != ""


@pytest.mark.parametrize(
    "api_datetime",
    [
        "2026-03-11T10:00:00+03:00",
        "2026-03-11T15:45:59+03:00",
        "2026-01-01T00:00:01+00:00",
        "2025-12-31T23:59:59+00:00",
    ],
)
@patch("program_files.api_client.requests.get")
def test_get_formatted_time_success(mock_get, api_datetime):
    mock_get.return_value.json.return_value = {"datetime": api_datetime}
    result = WorldTimeAPI.get_formatted_time()
    assert len(result) == 19
    datetime.strptime(result, "%Y-%m-%d %H:%M:%S")


@pytest.mark.parametrize("error_cls", [Exception, RuntimeError, requests.Timeout])
@patch("program_files.api_client.requests.get")
def test_get_formatted_time_fallback(mock_get, error_cls):
    mock_get.side_effect = error_cls("failure")
    result = WorldTimeAPI.get_formatted_time()
    datetime.strptime(result, "%Y-%m-%d %H:%M:%S")


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "5130904/20104", "faculty": {"name": "ИКНТ"}, "course": 3},
        {"name": "Group A", "faculty": {"name": "Faculty A"}, "course": 1},
        {"name": "Group B", "faculty": {"name": "Faculty B"}, "course": 2},
        {"name": "Group C", "faculty": {"name": "Faculty C"}, "course": 4},
        {"name": "Group D", "faculty": {"name": "Faculty D"}, "course": 5},
    ],
)
@patch("program_files.api_client.requests.get")
def test_get_group_info_success(mock_get, payload):
    mock_get.return_value.json.return_value = payload
    mock_get.return_value.raise_for_status.return_value = None

    result = ScheduleAPI.get_group_info(40520)
    assert result["name"] == payload["name"]
    assert result["faculty"] == payload["faculty"]["name"]
    assert result["course"] == payload["course"]


@pytest.mark.parametrize(
    "error",
    [
        requests.exceptions.RequestException("generic"),
        requests.exceptions.Timeout("timeout"),
        requests.exceptions.ConnectionError("connection"),
    ],
)
@patch("program_files.api_client.requests.get")
def test_get_group_info_fallback(mock_get, error):
    mock_get.side_effect = error
    result = ScheduleAPI.get_group_info(1)

    assert "name" in result
    assert "faculty" in result
    assert "course" in result


@pytest.mark.parametrize(
    "lesson_payload,expected_room,expected_teacher",
    [
        (
            {
                "time_start": "09:00",
                "time_end": "10:30",
                "subject": "Math",
                "typeObj": {"abbr": "Лек"},
                "auditories": [{"building": {"name": "B1"}, "name": "101"}],
                "teachers": [{"full_name": "Иванов И.И."}],
                "lms_url": "http://lms/a",
            },
            "B1 101",
            "Иванов И.И.",
        ),
        (
            {
                "time_start": "11:00",
                "time_end": "12:30",
                "subject": "Physics",
                "typeObj": {"abbr": "Пр"},
                "auditories": [],
                "teachers": [],
                "lms_url": "",
            },
            "Не указано",
            "Не указан",
        ),
        (
            {
                "time_start": "13:00",
                "time_end": "14:30",
                "subject": "Biology",
                "typeObj": {},
                "teachers": [{"full_name": "Петров П.П."}],
            },
            "Не указано",
            "Петров П.П.",
        ),
        (
            {
                "time_start": "15:00",
                "time_end": "16:30",
                "subject": "History",
                "typeObj": {"abbr": "Лаб"},
                "auditories": [{"building": {}, "name": "220"}],
                "teachers": [{}],
            },
            "220",
            "Не указан",
        ),
        (
            {
                "time_start": "17:00",
                "time_end": "18:30",
                "subject": "English",
                "typeObj": {"abbr": "Лек"},
                "auditories": [{"building": {"name": "Main"}, "name": ""}],
                "teachers": [{"full_name": ""}],
            },
            "Main",
            "",
        ),
        (
            {
                "time_start": "09:30",
                "time_end": "11:00",
                "subject": "CS",
                "typeObj": {"abbr": "Лек"},
                "auditories": [{"building": {"name": "D"}, "name": "404"}],
                "teachers": [{"full_name": "Coder"}],
                "lms_url": "https://lms/cs",
            },
            "D 404",
            "Coder",
        ),
        (
            {
                "time_start": "08:00",
                "time_end": "09:00",
                "subject": "PE",
                "typeObj": {"abbr": "Практ"},
                "auditories": [{"building": {"name": "Gym"}, "name": "1"}],
                "teachers": [{"full_name": "Coach"}],
            },
            "Gym 1",
            "Coach",
        ),
        (
            {
                "time_start": "19:00",
                "time_end": "20:00",
                "subject": "Art",
                "typeObj": {"abbr": "Сем"},
                "auditories": None,
                "teachers": None,
            },
            "Не указано",
            "Не указан",
        ),
    ],
)
@patch("program_files.api_client.requests.get")
def test_get_group_schedule_success(mock_get, lesson_payload, expected_room, expected_teacher):
    payload = {
        "week": {"date_start": "2026-03-10", "date_end": "2026-03-16", "is_odd": False},
        "days": [
            {
                "weekday": 1,
                "date": "2026-03-10",
                "lessons": [lesson_payload],
            }
        ],
    }

    mock_get.return_value.json.return_value = payload
    mock_get.return_value.raise_for_status.return_value = None

    result = ScheduleAPI.get_group_schedule(40520, date="2026-03-10")
    lesson = result["days"][0]["lessons"][0]

    assert result["week"]["date_start"] == "2026-03-10"
    assert lesson["room"] == expected_room
    assert lesson["teacher"] == expected_teacher


@patch("program_files.api_client.requests.get")
def test_get_group_schedule_uses_current_date_when_missing(mock_get):
    payload = {"week": {}, "days": []}
    mock_get.return_value.json.return_value = payload
    mock_get.return_value.raise_for_status.return_value = None

    ScheduleAPI.get_group_schedule(40520)

    called_kwargs = mock_get.call_args.kwargs
    assert "params" in called_kwargs
    assert "date" in called_kwargs["params"]


@pytest.mark.parametrize(
    "error",
    [
        requests.exceptions.RequestException("generic"),
        requests.exceptions.Timeout("timeout"),
        requests.exceptions.ConnectionError("connection"),
    ],
)
@patch("program_files.api_client.requests.get")
def test_get_group_schedule_fallback(mock_get, error):
    mock_get.side_effect = error

    result = ScheduleAPI.get_group_schedule(40520)
    assert "week" in result
    assert "days" in result
    assert len(result["days"]) >= 1
    assert len(result["days"][0]["lessons"]) >= 1

