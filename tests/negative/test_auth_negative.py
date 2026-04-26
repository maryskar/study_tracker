def test_register_rejects_duplicate_username(auth_manager):
    username = "dup_user"

    assert auth_manager.register(username, "pass1") is True
    assert auth_manager.register(username, "pass2") is False


def test_login_rejects_wrong_password(auth_manager):
    auth_manager.register("neg_user", "correct1")
    assert auth_manager.login("neg_user", "wrong1") is False


def test_login_unknown_user_returns_false(auth_manager):
    assert auth_manager.login("missing_user", "any_password") is False
