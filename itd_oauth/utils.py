from base64 import urlsafe_b64decode
from json import loads
from time import time


def decode_jwt_payload(jwt_token: str) -> dict:
    parts = jwt_token.split(".")
    if len(parts) != 3:
        raise ValueError("Not enough parts in access token")
    payload = parts[1]
    payload += "=" * ((4 - len(payload) % 4) % 4)
    decoded = urlsafe_b64decode(payload).decode("utf-8")
    return loads(decoded)


def is_token_expired(token: str) -> bool:
    return time() > decode_jwt_payload(token)["exp"]
