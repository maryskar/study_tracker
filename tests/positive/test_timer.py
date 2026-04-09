from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest


@pytest.mark.parametrize("mode", ["pomodoro", "short_break", "long_break"])
def test_start_session_adds_timer_job_for_countdown(timer_manager, mock_db, mode):
    ui_callback = MagicMock()
    timer_manager.start_session(user_id=7, mode=mode, update_ui=ui_callback)

    assert timer_manager.running is True
    assert timer_manager.current_mode == mode
    assert timer_manager.session_id == 101
    assert timer_manager.scheduler.jobs[-1]["func"] == timer_manager._update_timer


def test_start_session_adds_stopwatch_job(timer_manager, mock_db):
    ui_callback = MagicMock()
    timer_manager.start_session(user_id=11, mode="stopwatch", update_ui=ui_callback)

    assert timer_manager.running is True
    assert timer_manager.current_mode == "stopwatch"
    assert timer_manager.scheduler.jobs[-1]["func"] == timer_manager._update_stopwatch


@pytest.mark.parametrize("elapsed_seconds", [1, 1500])
def test_update_timer_sends_remaining_time(timer_manager, elapsed_seconds):
    timer_manager.current_mode = "pomodoro"
    timer_manager.running = True
    timer_manager.app_running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=elapsed_seconds)

    update_ui = MagicMock()
    timer_manager._update_timer(update_ui)

    update_ui.assert_called_once()
    rendered = update_ui.call_args.args[0]
    assert len(rendered) == 5
    assert ":" in rendered


@pytest.mark.parametrize("elapsed_seconds", [0, -5])
def test_update_timer_sends_negative_time(timer_manager, elapsed_seconds):
    timer_manager.current_mode = "pomodoro"
    timer_manager.running = True
    timer_manager.app_running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=elapsed_seconds)

    update_ui = MagicMock()
    timer_manager._update_timer(update_ui)

    update_ui.assert_called_once()
    rendered = update_ui.call_args.args[0]
    assert len(rendered) == 5
    assert ":" in rendered

@pytest.mark.parametrize("elapsed_seconds", [1, 10])
def test_update_stopwatch_formats_elapsed_time(timer_manager, elapsed_seconds):
    timer_manager.running = True
    timer_manager.app_running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=elapsed_seconds)

    update_ui = MagicMock()
    timer_manager._update_stopwatch(update_ui)

    update_ui.assert_called_once()
    assert ":" in update_ui.call_args.args[0]


@pytest.mark.parametrize("_case", [1, 2])
def test_complete_session_adds_achievement_for_pomodoro(timer_manager, mock_db, _case, monkeypatch):
    timer_manager.current_mode = "pomodoro"
    timer_manager.user_id = 7
    timer_manager.running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=30)
    timer_manager.session_id = 12

    stop = MagicMock()
    monkeypatch.setattr(timer_manager, "stop_timer", stop)

    timer_manager._complete_session()

    stop.assert_called_once()
    mock_db.add_achievement.assert_called_once()
    timer_manager.update_callback.assert_called_once()


@pytest.mark.parametrize("mode", ["short_break", "long_break"])
def test_complete_session_no_achievement_for_non_pomodoro(timer_manager, mock_db, mode, monkeypatch):
    timer_manager.current_mode = mode
    timer_manager.user_id = 7
    timer_manager.running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=30)
    timer_manager.session_id = 13

    stop = MagicMock()
    monkeypatch.setattr(timer_manager, "stop_timer", stop)

    timer_manager._complete_session()

    stop.assert_called_once()
    mock_db.add_achievement.assert_not_called()


@pytest.mark.parametrize("duration", [1, 30, 300])
def test_stop_timer_updates_session_and_clears_jobs(timer_manager, mock_db, duration):
    timer_manager.running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=duration)
    timer_manager.session_id = 101

    timer_manager.stop_timer()

    assert timer_manager.running is False
    mock_db.update_session.assert_called_once()
    assert timer_manager.scheduler.remove_all_jobs_calls == 1
