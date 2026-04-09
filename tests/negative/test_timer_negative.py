from unittest.mock import MagicMock

import pytest

import program_files.timer as timer_module


@pytest.mark.parametrize("running,app_running", [(False, True), (True, False)])
def test_update_timer_skips_when_not_active(timer_manager, running, app_running):
    timer_manager.current_mode = "pomodoro"
    timer_manager.running = running
    timer_manager.app_running = app_running
    timer_manager.start_time = timer_module.datetime.now()

    update_ui = MagicMock()
    timer_manager._update_timer(update_ui)
    update_ui.assert_not_called()


@pytest.mark.parametrize("_case", [1, 2])
def test_update_stopwatch_handles_exceptions(timer_manager, _case, monkeypatch):
    timer_manager.running = True
    timer_manager.app_running = True

    class BrokenDateTime:
        @classmethod
        def now(cls):
            raise RuntimeError("clock error")

    monkeypatch.setattr(timer_module, "datetime", BrokenDateTime)
    update_ui = MagicMock()
    timer_manager._update_stopwatch(update_ui)
    update_ui.assert_not_called()


@pytest.mark.parametrize("_case", [1, 2])
def test_stop_timer_noop_when_not_running(timer_manager, mock_db, _case):
    timer_manager.running = False
    timer_manager.stop_timer()

    mock_db.update_session.assert_not_called()
    assert timer_manager.scheduler.remove_all_jobs_calls == 0
