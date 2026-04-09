import pytest


@pytest.mark.parametrize(
    "username,password",
    [
        ("dup_a", "pass1"),
        ("dup_b", "pass2"),
        ("dup_c", "pass3"),
        ("dup_d", "pass4"),
    ],
)
def test_register_rejects_duplicate_username(auth_manager, username, password):
    assert auth_manager.register(username, password) is True
    assert auth_manager.register(username, password + "_new") is False


@pytest.mark.parametrize(
    "username,correct_password,wrong_password",
    [
        ("neg_1", "correct1", "wrong1"),
        ("neg_2", "correct2", "wrong2"),
        ("neg_3", "correct3", "wrong3"),
        ("neg_4", "correct4", "wrong4"),
        ("neg_5", "correct5", "wrong5"),
    ],
)
def test_login_rejects_wrong_password(auth_manager, username, correct_password, wrong_password):
    auth_manager.register(username, correct_password)
    assert auth_manager.login(username, wrong_password) is False


@pytest.mark.parametrize("username", ["missing_1", "missing_2", "missing_3", "missing_4"])
def test_login_unknown_user_returns_false(auth_manager, username):
    assert auth_manager.login(username, "any_password") is False
