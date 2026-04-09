from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt


@pytest.mark.parametrize(
    "username,password",
    [
        ("alice", "password123"),
        ("bob_01", "StrongPass!@#"),
        ("student", "abcDEF123"),
        ("user01", "qwertyQWERTY"),
        ("name.with.dot", "Pa$$w0rd"),
        ("name-with-dash", "dash-pass-123"),
        ("name123", "1234567890"),
        ("minimal", "min-pass"),
    ],
)
def test_register_accepts_valid_credentials(auth_manager, username, password):
    assert auth_manager.register(username, password) is True


@pytest.mark.parametrize(
    "username,password",
    [
        ("login_ok_1", "secret_1"),
        ("login_ok_2", "secret_2"),
        ("login_ok_3", "secret_3"),
        ("login_ok_4", "secret_4"),
    ],
)
def test_login_success_returns_expected_shape(auth_manager, username, password):
    auth_manager.register(username, password)
    login_data = auth_manager.login(username, password)

    assert isinstance(login_data, dict)
    assert {"id", "username", "token"}.issubset(login_data)
    assert login_data["username"] == username


@pytest.mark.parametrize("user_id", [1, 42, 9999])
def test_create_access_token_contains_user_id_and_expiration(auth_manager, user_id):
    token = auth_manager.create_access_token(user_id)
    payload = jwt.decode(
        token,
        auth_manager.SECRET_KEY,
        algorithms=[auth_manager.ALGORITHM],
    )

    assert payload["sub"] == str(user_id)

    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    assert exp > now
    assert exp <= now + timedelta(hours=25)


def test_register_hashes_password(auth_manager, isolated_db):
    raw_password = "dont_store_me"
    auth_manager.register("hash_user", raw_password)

    user = isolated_db.get_user("hash_user")
    assert user is not None
    assert user[2] != raw_password
    assert raw_password not in user[2]
