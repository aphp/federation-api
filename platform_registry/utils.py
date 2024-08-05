import secrets


def generate_key() -> str:
    return secrets.token_urlsafe(32)
