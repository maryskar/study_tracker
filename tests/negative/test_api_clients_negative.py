from datetime import datetime
from unittest.mock import patch

import pytest
import requests

from program_files.api_client import MotivationAPI, ScheduleAPI, WorldTimeAPI


@pytest.mark.parametrize("error_cls", [Exception, RuntimeError, ValueError])
@patch("program_files.api_client.requests.get")
def test_get_quote_fallback_on_error(mock_get, error_cls):
    mock_get.side_effect = error_cls("network down")
    result = MotivationAPI.get_quote()
    assert isinstance(result, str)
    assert result != ""


@pytest.mark.parametrize("error_cls", [Exception, RuntimeError, requests.Timeout])
@patch("program_files.api_client.requests.get")
def test_get_formatted_time_fallback(mock_get, error_cls):
    mock_get.side_effect = error_cls("failure")
    result = WorldTimeAPI.get_formatted_time()
    datetime.strptime(result, "%Y-%m-%d %H:%M:%S")


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
