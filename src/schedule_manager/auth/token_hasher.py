import hashlib
import hmac


def hash_token(token: str) -> str:
    """Hash a token before storing it; the original token cannot be recovered."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token(token_hash: str, token: str) -> bool:
    """Compare a candidate token to a stored hash without revealing the token."""
    return hmac.compare_digest(token_hash, hash_token(token))
