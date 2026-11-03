import hashlib

from schedule_manager.auth.token_hasher import hash_token, verify_token


def test_hash_token_uses_sha256_and_can_be_verified() -> None:
    token = "opaque-session-token"

    token_hash = hash_token(token)

    assert token_hash == hashlib.sha256(token.encode("utf-8")).hexdigest()
    assert verify_token(token_hash, token)
    assert not verify_token(token_hash, "different-token")
