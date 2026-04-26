def test_register_rejects_duplicate_username(auth_manager):
    username = "dup_user"

    assert auth_manager.register(username, "pass1") is True
    assert auth_manager.register(username, "pass2") is False


def test_register_rejects_empty_credentials(auth_manager):
    assert auth_manager.register("", "pass1") is False
    assert auth_manager.register("user", "") is False
    assert auth_manager.register("   ", "pass1") is False
    assert auth_manager.register("user", "   ") is False


def test_login_rejects_wrong_password(auth_manager):
    auth_manager.register("neg_user", "correct1")
    assert auth_manager.login("neg_user", "wrong1") is False


def test_login_unknown_user_returns_false(auth_manager):
    assert auth_manager.login("missing_user", "any_password") is False


def test_login_rejects_empty_credentials(auth_manager):
    assert auth_manager.login("", "pass1") is False
    assert auth_manager.login("user", "") is False
    assert auth_manager.login("   ", "pass1") is False
    assert auth_manager.login("user", "   ") is False


def test_login_returns_false_for_invalid_stored_hash(auth_manager, isolated_db):
    isolated_db.create_user("broken_hash_user", "not-a-valid-hash")
    assert auth_manager.login("broken_hash_user", "any_password") is False
