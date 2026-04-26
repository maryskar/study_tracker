from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt


@pytest.mark.parametrize(
    "username,raw_password",
    [
        ("alice", "password123"),
        ("bob_01", "StrongPass!@#"),
        ("student", "abcDEF123"),
        ("name.with.dot", "Pa$$w0rd"),
        ("name-with-dash", "dash-pass-123"),
    ],
)
def test_register_creates_user_with_hashed_password(auth_manager, isolated_db, username, raw_password):
    assert auth_manager.register(username, raw_password) is True

    user = isolated_db.get_user(username)
    assert user is not None
    assert user[1] == username
    assert user[2] != raw_password


@pytest.mark.parametrize(
    "username,password",
    [
        ("login_ok_1", "secret_1"),
        ("login_ok_2", "secret_2"),
        ("login_ok_3", "secret_3"),
        ("login_ok_4", "secret_4"),
    ],
)
def test_login_success_returns_user_payload_with_valid_token(auth_manager, username, password):
    auth_manager.register(username, password)

    login_data = auth_manager.login(username, password)
    payload = jwt.decode(
        login_data["token"],
        auth_manager.SECRET_KEY,
        algorithms=[auth_manager.ALGORITHM],
    )

    assert isinstance(login_data, dict)
    assert {"id", "username", "token"}.issubset(login_data)
    assert login_data["username"] == username
    assert payload["sub"] == str(login_data["id"])


@pytest.mark.parametrize("user_id", [1, 42, 9999])
def test_create_access_token_contains_user_id_and_expiration(auth_manager, user_id):
    token = auth_manager.create_access_token(user_id)
    payload = jwt.decode(
        token,
        auth_manager.SECRET_KEY,
        algorithms=[auth_manager.ALGORITHM],
    )

    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)

    assert payload["sub"] == str(user_id)
    assert exp > now
    assert exp <= now + timedelta(hours=25)
