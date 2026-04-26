# test_database.py
import pytest

# ============================================================
# 1. ТЕСТЫ ПОЛЬЗОВАТЕЛЕЙ (User) — 9 сценариев
# ============================================================

def test_create_user_valid_persists(isolated_db):
    """
    КЛАСС: ДОПУСТИМЫЙ (обычный представитель)
    ГРАНИЦЫ: нет
    """
    assert isolated_db.create_user("valid_user", "hash123") is True
    user = isolated_db.get_user("valid_user")
    assert user is not None
    assert user[1] == "valid_user"
    assert user[2] == "hash123"


@pytest.mark.parametrize("username,password_hash", [
    (None, "hash"),      # КЛАСС: НЕДОПУСТИМЫЙ (username = None)
    ("user", None),      # КЛАСС: НЕДОПУСТИМЫЙ (password_hash = None)
    (None, None),        # КЛАСС: НЕДОПУСТИМЫЙ (оба None)
])
def test_create_user_none_values_returns_false(isolated_db, username, password_hash):
    """
    КЛАСС: НЕДОПУСТИМЫЙ (None-значения)
    ГРАНИЦЫ: None — граница между «есть значение» и «нет значения»
    """
    assert isolated_db.create_user(username, password_hash) is False


def test_create_user_duplicate_username_fails(isolated_db):
    """
    КЛАСС: НЕДОПУСТИМЫЙ (нарушение UNIQUE constraint)
    ГРАНИЦЫ: нет
    """
    isolated_db.create_user("duplicate_user", "hash1")
    assert isolated_db.create_user("duplicate_user", "hash2") is False


def test_get_user_existing_returns_user(isolated_db):
    """
    КЛАСС: ДОПУСТИМЫЙ (существующий пользователь)
    """
    isolated_db.create_user("existing_user", "hash")
    user = isolated_db.get_user("existing_user")
    assert user is not None
    assert user[1] == "existing_user"


def test_get_user_nonexistent_returns_none(isolated_db):
    """
    КЛАСС: НЕДОПУСТИМЫЙ (несуществующий пользователь)
    """
    assert isolated_db.get_user("ghost") is None


def test_get_user_empty_string_returns_none(isolated_db):
    """
    КЛАСС: ГРАНИЧНЫЙ (пустая строка)
    ГРАНИЦЫ: "" — граница между «есть username» и «нет username»
    """
    assert isolated_db.get_user("") is None


# ============================================================
# 2. ТЕСТЫ СЕССИЙ (Session) — 11 сценариев
# ============================================================

@pytest.fixture
def user_id(isolated_db):
    isolated_db.create_user("session_user", "hash")
    return isolated_db.get_user("session_user")[0]


def test_create_session_returns_positive_int_id(user_id, isolated_db):
    """
    КЛАСС: ДОПУСТИМЫЙ
    ГРАНИЦЫ: session_id > 0
    """
    session_id = isolated_db.create_session(user_id, "2026-03-01 09:00:00", "pomodoro")
    assert isinstance(session_id, int)
    assert session_id > 0


@pytest.mark.parametrize("session_type", ["pomodoro", "stopwatch", "short_break", "long_break"])
def test_create_session_persists_data(user_id, isolated_db, session_type):
    """
    КЛАССЫ: ВСЕ ДОПУСТИМЫЕ ЗНАЧЕНИЯ session_type (каждый тип — отдельный сценарий)
    """
    start = "2026-03-01 09:00:00"
    session_id = isolated_db.create_session(user_id, start, session_type)
    
    sessions = isolated_db.get_user_sessions(user_id)
    session = next((s for s in sessions if s[0] == session_id), None)
    assert session is not None
    assert session[2] == start
    assert session[5] == session_type


@pytest.fixture
def session_id(user_id, isolated_db):
    session_id = isolated_db.create_session(user_id, "2026-03-01 08:00:00", "pomodoro")
    return session_id


@pytest.mark.parametrize("duration", [0, 1, 3600, 3601])
def test_update_session_duration_boundaries(user_id, session_id, isolated_db, duration):
    """
    КЛАСС: ГРАНИЧНЫЕ ЗНАЧЕНИЯ длительности
    ГРАНИЦЫ:
        - 0 до нижней границы (недопустимое)
        - 1 нижняя граница (минимальное допустимое)
        - 3600 верхняя граница (допустимое, 1 час)
        - 3601 после верхней границы (недопустимое)
    """
    isolated_db.update_session(session_id, "2026-03-01 09:00:00", duration)
    updated = [row for row in isolated_db.get_user_sessions(user_id) if row[0] == session_id][0]
    assert updated[4] == duration


def test_update_session_nonexistent_id_does_not_fail(isolated_db):
    """
    КЛАСС: НЕДОПУСТИМЫЙ (несуществующий ID)
    ГРАНИЦЫ: 99999 — заведомо несуществующий ID
    """
    isolated_db.update_session(99999, "2026-03-01 09:00:00", 3600)


def test_get_user_sessions_returns_sorted_desc(user_id, isolated_db):
    """
    КЛАСС: ДОПУСТИМЫЙ (проверка сортировки ORDER BY start_time DESC)
    """
    times = ["2026-03-01 09:00:00", "2026-03-01 08:00:00", "2026-03-01 10:00:00"]
    for t in times:
        isolated_db.create_session(user_id, t, "pomodoro")
    
    sessions = isolated_db.get_user_sessions(user_id)
    start_times = [s[2] for s in sessions]
    assert start_times == sorted(start_times, reverse=True)


def test_get_user_sessions_empty_returns_empty_list(user_id, isolated_db):
    """
    КЛАСС: ГРАНИЧНЫЙ (у пользователя нет сессий)
    ГРАНИЦЫ: [] — пустой список
    """
    assert isolated_db.get_user_sessions(user_id) == []


# ============================================================
# 3. ТЕСТЫ ДОСТИЖЕНИЙ (Achievement) — 4 сценария
# ============================================================

def test_add_achievement_persists(user_id, isolated_db):
    """
    КЛАСС: ДОПУСТИМЫЙ (обычное достижение)
    """
    isolated_db.add_achievement(user_id, "Title", "Desc")
    achievements = isolated_db.get_achievements(user_id)
    assert any(a[2] == "Title" and a[3] == "Desc" for a in achievements)


def test_get_achievements_empty_returns_empty_list(user_id, isolated_db):
    """
    КЛАСС: ГРАНИЧНЫЙ (отсутствие достижений)
    ГРАНИЦЫ: [] — пустой список
    """
    assert isolated_db.get_achievements(user_id) == []


def test_get_achievements_multiple_returns_all(user_id, isolated_db):
    """
    КЛАСС: ДОПУСТИМЫЙ (множественные достижения)
    """
    isolated_db.add_achievement(user_id, "First", "Desc1")
    isolated_db.add_achievement(user_id, "Second", "Desc2")
    isolated_db.add_achievement(user_id, "Third", "Desc3")
    
    achievements = isolated_db.get_achievements(user_id)
    assert len(achievements) == 3
    titles = [a[2] for a in achievements]
    assert all(t in titles for t in ["First", "Second", "Third"])


def test_add_achievement_empty_title_persists(user_id, isolated_db):
    """
    КЛАСС: ГРАНИЧНЫЙ (пустой заголовок)
    ГРАНИЦЫ: "" — пустая строка
    """
    isolated_db.add_achievement(user_id, "", "Desc")
    achievements = isolated_db.get_achievements(user_id)
    assert any(a[3] == "Desc" for a in achievements)


# ============================================================
# 4. ТЕСТЫ get_month_sessions — 3 сценария
# ============================================================

def test_get_month_sessions_filters_by_month_and_year(user_id, isolated_db):
    """
    КЛАССЫ: фильтрация по месяцу и году
    Проверяем:
        - январь 2026 (с данными) 1 сессия
        - февраль 2026 (без данных) 0 сессий (граница)
        - март 2026 (несколько сессий) 2 сессии
        - декабрь 2025 (другой год) 1 сессия (проверка YEAR)
    """
    sessions = [
        "2026-01-15 10:00:00",
        "2026-03-05 12:00:00",
        "2026-03-25 13:00:00",
        "2025-12-31 23:00:00",
    ]
    for t in sessions:
        isolated_db.create_session(user_id, t, "pomodoro")
    
    assert len(isolated_db.get_month_sessions(user_id, 1, 2026)) == 1
    assert len(isolated_db.get_month_sessions(user_id, 2, 2026)) == 0
    assert len(isolated_db.get_month_sessions(user_id, 3, 2026)) == 2
    assert len(isolated_db.get_month_sessions(user_id, 12, 2025)) == 1


def test_get_month_sessions_nonexistent_user_returns_empty(isolated_db):
    """
    КЛАСС: НЕДОПУСТИМЫЙ (несуществующий пользователь)
    ГРАНИЦЫ: 99999 — несуществующий ID
    """
    assert isolated_db.get_month_sessions(99999, 1, 2026) == []


def test_get_month_sessions_isolated_by_user(isolated_db):
    """
    КЛАСС: ИЗОЛЯЦИЯ ПОЛЬЗОВАТЕЛЕЙs
    Проверяем, что сессии user_a не попадают в выборку user_b
    ГРАНИЦЫ: нет
    """
    isolated_db.create_user("user_a", "hash")
    isolated_db.create_user("user_b", "hash")
    uid_a = isolated_db.get_user("user_a")[0]
    uid_b = isolated_db.get_user("user_b")[0]
    
    isolated_db.create_session(uid_a, "2026-03-10 09:00:00", "pomodoro")
    isolated_db.create_session(uid_a, "2026-03-15 10:00:00", "pomodoro")
    isolated_db.create_session(uid_b, "2026-03-10 09:00:00", "pomodoro")
    
    assert len(isolated_db.get_month_sessions(uid_a, 3, 2026)) == 2
    assert len(isolated_db.get_month_sessions(uid_b, 3, 2026)) == 1
    assert len(isolated_db.get_month_sessions(uid_a, 4, 2026)) == 0
    assert len(isolated_db.get_month_sessions(uid_b, 4, 2026)) == 0
