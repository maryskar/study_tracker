from datetime import datetime

import pytest


@pytest.mark.parametrize(
    "username,password_hash",
    [
        ("u_create_1", "h1"),
        ("u_create_2", "h2"),
        ("u_create_3", "h3"),
        ("u_create_4", "h4"),
        ("u_create_5", "h5"),
        ("u_create_6", "h6"),
    ],
)
def test_create_user_persists_user(isolated_db, username, password_hash):
    assert isolated_db.create_user(username, password_hash) is True
    user = isolated_db.get_user(username)
    assert user is not None
    assert user[1] == username


@pytest.mark.parametrize(
    "username,password_hash",
    [
        (None, "hash"),
        ("user_none_hash", None),
        (None, None),
    ],
)
def test_create_user_invalid_data_returns_false(isolated_db, username, password_hash):
    assert isolated_db.create_user(username, password_hash) is False


@pytest.mark.parametrize("username", ["ghost_1", "ghost_2"])
def test_get_user_returns_none_for_missing_user(isolated_db, username):
    assert isolated_db.get_user(username) is None


@pytest.mark.parametrize(
    "session_type,start_time",
    [
        ("pomodoro", "2026-03-01 09:00:00"),
        ("stopwatch", "2026-03-01 09:30:00"),
        ("short_break", "2026-03-01 10:00:00"),
        ("long_break", "2026-03-01 10:30:00"),
        ("pomodoro", "2026-03-01 11:00:00"),
    ],
)
def test_create_session_persists_data(isolated_db, session_type, start_time):
    isolated_db.create_user("sess_user", "hash")
    user_id = isolated_db.get_user("sess_user")[0]

    session_id = isolated_db.create_session(user_id, start_time, session_type)
    assert isinstance(session_id, int)

    sessions = isolated_db.get_user_sessions(user_id)
    assert any(session[0] == session_id for session in sessions)


@pytest.mark.parametrize(
    "duration",
    [1, 30, 1500, 3600],
)
def test_update_session_updates_end_time_and_duration(isolated_db, duration):
    isolated_db.create_user("upd_user", "hash")
    user_id = isolated_db.get_user("upd_user")[0]

    session_id = isolated_db.create_session(user_id, "2026-03-01 08:00:00", "pomodoro")
    end_time = "2026-03-01 09:00:00"
    isolated_db.update_session(session_id, end_time, duration)

    updated = [row for row in isolated_db.get_user_sessions(user_id) if row[0] == session_id][0]
    assert updated[3] == end_time
    assert updated[4] == duration


@pytest.mark.parametrize(
    "time_values",
    [
        ["2026-03-01 07:00:00", "2026-03-01 08:00:00", "2026-03-01 09:00:00"],
        ["2026-03-03 11:00:00", "2026-03-01 11:00:00", "2026-03-02 11:00:00"],
        ["2026-01-01 00:00:03", "2026-01-01 00:00:02", "2026-01-01 00:00:01"],
    ],
)
def test_get_user_sessions_sorted_desc_by_start_time(isolated_db, time_values):
    isolated_db.create_user("sort_user", "hash")
    user_id = isolated_db.get_user("sort_user")[0]

    for value in time_values:
        isolated_db.create_session(user_id, value, "pomodoro")

    sessions = isolated_db.get_user_sessions(user_id)
    start_times = [item[2] for item in sessions]
    assert start_times == sorted(start_times, reverse=True)


@pytest.mark.parametrize(
    "title,description",
    [
        ("A1", "D1"),
        ("A2", "D2"),
        ("A3", "D3"),
        ("A4", "D4"),
    ],
)
def test_add_achievement_persists_achievement(isolated_db, title, description):
    isolated_db.create_user("ach_user", "hash")
    user_id = isolated_db.get_user("ach_user")[0]

    isolated_db.add_achievement(user_id, title, description)
    achievements = isolated_db.get_achievements(user_id)

    assert any(item[2] == title and item[3] == description for item in achievements)


@pytest.mark.parametrize(
    "month,year,expected_count",
    [
        (1, 2026, 1),
        (2, 2026, 1),
        (3, 2026, 2),
        (12, 2025, 1),
    ],
)
def test_get_month_sessions_filters_by_month_and_year(isolated_db, month, year, expected_count):
    isolated_db.create_user("month_user", "hash")
    user_id = isolated_db.get_user("month_user")[0]

    sessions = [
        "2026-01-15 10:00:00",
        "2026-02-20 11:00:00",
        "2026-03-05 12:00:00",
        "2026-03-25 13:00:00",
        "2025-12-31 23:00:00",
    ]
    for start_time in sessions:
        isolated_db.create_session(user_id, start_time, "pomodoro")

    result = isolated_db.get_month_sessions(user_id, month, year)
    assert len(result) == expected_count


@pytest.mark.parametrize("month", [3, 4])
def test_get_month_sessions_isolated_by_user(isolated_db, month):
    isolated_db.create_user("month_a", "hash")
    isolated_db.create_user("month_b", "hash")
    user_a = isolated_db.get_user("month_a")[0]
    user_b = isolated_db.get_user("month_b")[0]

    isolated_db.create_session(user_a, "2026-03-10 09:00:00", "pomodoro")
    isolated_db.create_session(user_b, "2026-03-10 09:00:00", "pomodoro")

    result_a = isolated_db.get_month_sessions(user_a, month, 2026)
    if month == 3:
        assert len(result_a) == 1
    else:
        assert len(result_a) == 0


def test_get_achievements_empty_returns_empty_list(isolated_db):
    isolated_db.create_user("empty_ach", "hash")
    user_id = isolated_db.get_user("empty_ach")[0]
    assert isolated_db.get_achievements(user_id) == []


def test_create_and_update_session_full_flow(isolated_db):
    isolated_db.create_user("flow_user", "hash")
    user_id = isolated_db.get_user("flow_user")[0]

    start_time = datetime(2026, 3, 11, 9, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime(2026, 3, 11, 9, 25, 0).strftime("%Y-%m-%d %H:%M:%S")

    session_id = isolated_db.create_session(user_id, start_time, "pomodoro")
    isolated_db.update_session(session_id, end_time, 1500)

    session = isolated_db.get_user_sessions(user_id)[0]
    assert session[2] == start_time
    assert session[3] == end_time
    assert session[4] == 1500
    assert session[5] == "pomodoro"

