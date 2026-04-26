from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
import program_files.timer as timer_module


# ============================================================================
# START_SESSION - Инициализация сессии
# ============================================================================

@pytest.mark.parametrize("mode", ["pomodoro", "short_break", "long_break"])
def test_start_timer_modes_creates_timer_job(timer_manager, mock_db, mode):
    """Режимы таймера (pomodoro, short_break, long_break) создают _update_timer"""
    ui_callback = MagicMock()
    timer_manager.start_session(user_id=7, mode=mode, update_ui=ui_callback)

    assert timer_manager.running is True
    assert timer_manager.current_mode == mode
    assert timer_manager.user_id == 7
    assert timer_manager.session_id == 101
    assert timer_manager.scheduler.jobs[-1]["func"] == timer_manager._update_timer


def test_start_stopwatch_mode_creates_stopwatch_job(timer_manager, mock_db):
    """Режим stopwatch создает _update_stopwatch вместо _update_timer"""
    ui_callback = MagicMock()
    timer_manager.start_session(user_id=11, mode="stopwatch", update_ui=ui_callback)

    assert timer_manager.running is True
    assert timer_manager.current_mode == "stopwatch"
    assert timer_manager.session_id == 101
    assert timer_manager.scheduler.jobs[-1]["func"] == timer_manager._update_stopwatch


def test_start_session_calls_db_create_session(timer_manager, mock_db):
    """Проверка вызова БД при запуске сессии"""
    timer_manager.start_session(user_id=5, mode="pomodoro", update_ui=MagicMock())
    
    mock_db.create_session.assert_called_once()
    args = mock_db.create_session.call_args[0]
    assert args[0] == 5
    assert args[2] == "pomodoro"


# ============================================================================
# UPDATE_TIMER - Обновление обратного отсчета (0-1500 секунд)
# ============================================================================

@pytest.mark.parametrize("elapsed_seconds", [-1, 0, 1, 1499, 1500, 1501])
def test_update_timer_remaining_time_and_completion(timer_manager, monkeypatch, elapsed_seconds):
    """Таймер показывает оставшееся время или завершает сессию"""
    timer_manager.current_mode = "pomodoro"
    timer_manager.running = True
    timer_manager.app_running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=elapsed_seconds)

    update_ui = MagicMock()
    complete_session = MagicMock()
    monkeypatch.setattr(timer_manager, "_complete_session", complete_session)
    
    timer_manager._update_timer(update_ui)

    if elapsed_seconds < 1500:
        # Таймер должен отправить время
        update_ui.assert_called_once()
        rendered = update_ui.call_args.args[0]
        assert len(rendered) == 5, f"Format should be MM:SS, got {rendered}"
        assert ":" in rendered
    else:
        # Время истекло или переполнено - завершить сессию
        update_ui.assert_not_called()
        complete_session.assert_called_once()


@pytest.mark.parametrize("mode, duration", [
    ("pomodoro", 1500),
    ("short_break", 300),
    ("long_break", 900),
])
@pytest.mark.parametrize("elapsed_seconds", [-1, 0, 1,])
def test_update_timer_different_modes_beginning(timer_manager, monkeypatch, mode, duration, elapsed_seconds):
    """Разные режимы показывают время в начале сессии"""
    timer_manager.current_mode = mode
    timer_manager.running = True
    timer_manager.app_running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=max(0, elapsed_seconds))

    update_ui = MagicMock()
    timer_manager._update_timer(update_ui)

    update_ui.assert_called_once()
    rendered = update_ui.call_args.args[0]
    assert ":" in rendered


@pytest.mark.parametrize("mode,duration", [
    ("pomodoro", 1500),
    ("short_break", 300),
    ("long_break", 900),
])
@pytest.mark.parametrize("offset", [-1, 0, 1,])
def test_update_timer_completion_at_each_mode(timer_manager, monkeypatch, mode, duration, offset):
    """Каждый режим завершается при его длительности + offset"""
    timer_manager.current_mode = mode
    timer_manager.running = True
    timer_manager.app_running = True
    elapsed = duration + offset
    timer_manager.start_time = datetime.now() - timedelta(seconds=elapsed)

    update_ui = MagicMock()
    complete_session = MagicMock()
    monkeypatch.setattr(timer_manager, "_complete_session", complete_session)
    
    timer_manager._update_timer(update_ui)

    if offset >= 0:
        # Время истекло
        complete_session.assert_called_once()
        update_ui.assert_not_called()
    else:
        # Время не истекло
        update_ui.assert_called_once()


# ============================================================================
# UPDATE_STOPWATCH - Обновление секундомера (0-3661+ секунд)
# ============================================================================
"""спросить у нейронки логику работы этой фигни"""
@pytest.mark.parametrize("elapsed_seconds", [0, 1, 59, 60, 61, 3599, 3600, 3661])
def test_stopwatch_formats_time_at_boundaries(timer_manager, elapsed_seconds):
    """Секундомер форматирует время при граничных и нормальных значениях"""
    timer_manager.running = True
    timer_manager.app_running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=elapsed_seconds)

    update_ui = MagicMock()
    timer_manager._update_stopwatch(update_ui)

    update_ui.assert_called_once()
    rendered = update_ui.call_args.args[0]
    assert ":" in rendered
    assert len(rendered) >= 7  # Минимум HH:MM:SS


# ============================================================================
# STOP_TIMER - Остановка таймера (1-3600 секунд)
# ============================================================================

@pytest.mark.parametrize("duration_seconds", [1, 3599, 3600, 3601])
def test_stop_timer_running_updates_session(timer_manager, mock_db, duration_seconds):
    """Остановка таймера обновляет сессию для различных длительностей"""
    timer_manager.running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=duration_seconds)
    timer_manager.session_id = 101

    timer_manager.stop_timer()

    assert timer_manager.running is False
    
    mock_db.update_session.assert_called_once()
    args = mock_db.update_session.call_args[0]
    assert args[0] == 101 


def test_stop_timer_removes_scheduler_jobs(timer_manager, mock_db):
    """Остановка удаляет все задачи из планировщика"""
    timer_manager.running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=10)
    timer_manager.session_id = 101

    timer_manager.stop_timer()

    assert timer_manager.scheduler.remove_all_jobs_calls == 1


def test_stop_timer_not_running_does_nothing(timer_manager, mock_db):
    """Остановка незапущенного таймера ничего не делает"""
    timer_manager.running = False

    timer_manager.stop_timer()

    mock_db.update_session.assert_not_called()
    assert timer_manager.scheduler.remove_all_jobs_calls == 0


def test_stop_timer_idempotent(timer_manager, mock_db):
    """Двойная остановка безопасна и не вызывает дополнительные действия"""
    timer_manager.running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=10)
    timer_manager.session_id = 101

    timer_manager.stop_timer()
    first_call_count = mock_db.update_session.call_count

    timer_manager.stop_timer()
    second_call_count = mock_db.update_session.call_count

    assert second_call_count == first_call_count


@pytest.mark.parametrize("elapsed_seconds", [0, 1])
def test_stop_timer_records_correct_duration(timer_manager, mock_db, elapsed_seconds):
    """Длительность сессии записывается корректно (допуск для timing)"""
    timer_manager.running = True
    timer_manager.start_time = datetime.now() - timedelta(seconds=elapsed_seconds)
    timer_manager.session_id = 101

    timer_manager.stop_timer()

    args = mock_db.update_session.call_args[0]
    recorded_duration = args[2]
    tolerance = 2  # 2 сек допуск
    assert elapsed_seconds - tolerance <= recorded_duration <= elapsed_seconds + tolerance