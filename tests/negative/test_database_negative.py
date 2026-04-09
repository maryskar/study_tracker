import pytest


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


def test_get_achievements_empty_returns_empty_list(isolated_db):
    isolated_db.create_user("empty_ach", "hash")
    user_id = isolated_db.get_user("empty_ach")[0]
    assert isolated_db.get_achievements(user_id) == []
