import pytest


def test_register_rejects_duplicate_username(auth_manager):
    username = "dup_user"

    assert auth_manager.register(username, "pass1") is True
    assert auth_manager.register(username, "pass2") is False


@pytest.mark.parametrize(
    "username,password",
    [
        ("", "pass1"),
        ("user", ""),
        ("   ", "pass1"),
        ("user", "   "),
    ],
)
def test_register_rejects_invalid_credentials(auth_manager, username, password):
    assert auth_manager.register(username, password) is False


def test_register_returns_false_when_password_hashing_fails(auth_manager, monkeypatch):
    def broken_hash(_password):
        raise RuntimeError("hash failed")

    monkeypatch.setattr(auth_manager.pwd_context, "hash", broken_hash)
    assert auth_manager.register("user", "pass1") is False


@pytest.mark.parametrize(
    "username,correct_password,wrong_password",
    [
        ("neg_user_1", "correct1", "wrong1"),
        ("neg_user_2", "correct2", "wrong2"),
        ("neg_user_3", "correct3", "wrong3"),
    ],
)
def test_login_rejects_wrong_password(auth_manager, username, correct_password, wrong_password):
    auth_manager.register(username, correct_password)
    assert auth_manager.login(username, wrong_password) is False


@pytest.mark.parametrize("username", ["missing_user_1", "missing_user_2"])
def test_login_unknown_user_returns_false(auth_manager, username):
    assert auth_manager.login(username, "any_password") is False


def test_login_rejects_invalid_credentials(auth_manager):
    assert auth_manager.login("", "pass1") is False


def test_login_returns_false_for_invalid_stored_hash(auth_manager, isolated_db):
    isolated_db.create_user("broken_hash_user", "not-a-valid-hash")
    assert auth_manager.login("broken_hash_user", "any_password") is False
