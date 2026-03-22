import pytest

from app.auth.utils import (
    decode_jwt,
    encode_jwt,
    hash_password,
    password_hasher,
    verify_password,
)


@pytest.mark.unit
def test_hash_password():
    hashed = hash_password("test")
    assert hashed
    assert hashed != "test"


@pytest.mark.unit
def test_verify_password():
    hashed = password_hasher.hash("test")
    assert verify_password("test", hashed)
    assert not verify_password("test1", hashed)


@pytest.mark.unit
def test_encode_decode_jwt():
    token = encode_jwt({"username": "test"})
    assert token

    payload = decode_jwt(token)
    assert payload.get("username")
    assert payload.get("username") == "test"
