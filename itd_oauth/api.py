from typing import TYPE_CHECKING, Any

from requests import post, request

from itd_oauth.exceptions import (
    InvalidCodeError,
    InvalidRefreshTokenError,
    SessionRevokedError
)

if TYPE_CHECKING:
    from itd_oauth.client import Client


def exchange_code(client: Client, code: str) -> dict:
    res = post(
        "https://auth.xn--d1ah4a.tech/oauth/token",
        json={
            "code": code,
            "client_id": client.client_id,
            "client_secret": client.client_secret
        }
    )
    data = res.json()
    if res.status_code == 400 and data.get("message") == "Invalid code":
        raise InvalidCodeError()

    return {
        "access_token": data["token"],
        "refresh_token": res.cookies["itd_oauth_refresh"],
        "expires_in": data["expires_in"] or 1200
    }


def refresh_token(client: Client, refresh_token: str) -> dict:
    res = post(
        "https://auth.xn--d1ah4a.tech/oauth/refresh",
        json={"client_id": client.client_id, "client_secret": client.client_secret},
        cookies={"itd_oauth_refresh": refresh_token}
    )
    data = res.json()
    if res.status_code == 401 and data.get("message") == "Invalid refresh token":
        raise InvalidRefreshTokenError
    if res.status_code == 401 and data.get("message") == "Session revoked":
        raise SessionRevokedError

    return {"token": data["token"], "expires_in": data["expires_in"] or 1200}


def proxy_request(
    token: str,
    method: str,
    url: str,
    *,
    data: Any = ...,
    files: Any | None = None,
    headers: dict[str, str | bytes] = {},
    json: Any | None = None,
    params: Any | None = None,
    proxies: dict[str, str] | None = None,
    timeout: int | float | tuple[int | float | None, int | float | None] | None = None
):
    url = url.replace("итд", "xn--d1ah4a")
    if url.startswith("https://xn--d1ah4a.com/api"):
        url = url.replace(
            "https://xn--d1ah4a.com/api", "https://auth.xn--d1ah4a.tech/proxy"
        )
    else:
        url = "https://auth.xn--d1ah4a.tech/proxy/" + url

    headers["Authorization"] = f"Bearer {token}"

    return request(
        method,
        url,
        data=data,
        files=files,
        headers=headers,
        json=json,
        params=params,
        proxies=proxies,
        timeout=timeout
    )
