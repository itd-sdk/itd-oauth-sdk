from typing import TYPE_CHECKING, Any, Literal

from itd_oauth.api import exchange_code, proxy_request, refresh_token
from itd_oauth.utils import decode_jwt_payload, is_token_expired

try:
    from fastapi import Header, HTTPException, Response

    FASTAPI = True
except ImportError:
    FASTAPI = False

try:
    from itd import ITDConfig

    ITD_SDK = True
except ImportError:
    ITD_SDK = False

SCOPE = Literal[
    "users",
    "posts",
    "comments",
    "notifications",
    "files",
    "reports",
    "hashtags",
    "search",
    "subscription",
    "verification",
    "platform"
]


class Client:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(
        self, scopes: str | SCOPE | list[SCOPE], redirect_uri: str | None = None
    ):
        if isinstance(scopes, list):
            scope = " ".join(scopes)
        else:
            scope = scopes
        return f"https://auth.xn--d1ah4a.tech/oauth/authorize?client_id={self.client_id}&scope={scope}{f'&redirect_uri={redirect_uri}' if redirect_uri else ''}"

    @property
    def url(self):
        return "https://auth.xn--d1ah4a.tech/proxy"

    if ITD_SDK:

        @property
        def sdk_config(self):
            return ITDConfig(
                url=self.url, refresh_token_cookie_name="itd_oauth_refresh"
            )

        def patch_config(self, config: "ITDConfig"):
            config.url = self.url
            config.refresh_token_cookie_name = "itd_oauth_refresh"

            return config
    else:

        @property
        def sdk_config(self):
            raise ImportError(
                "itd-sdk is required for client.sdk_config. Install via: uv add itd-oauth-sdk[itd-sdk]"
            )

        def patch_config(self, config: Any):
            raise ImportError(
                "itd-sdk is required for client.patch_config. Install via: uv add itd-oauth-sdk[itd-sdk]"
            )

    def exchange_code(self, code: str) -> dict:
        return exchange_code(self, code)

    def refresh_token(self, token: str) -> dict:
        return refresh_token(self, token)

    def proxy(
        self,
        access_token: str,
        method: str,
        url: str,
        *,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str | bytes] = {},
        json: Any | None = None,
        params: Any | None = None,
        proxies: dict[str, str] | None = None,
        timeout: int
        | float
        | tuple[int | float | None, int | float | None]
        | None = None
    ):
        return proxy_request(
            access_token,
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

    def proxy_with_refresh(
        self,
        refresh_token: str,
        method: str,
        url: str,
        *,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str | bytes] = {},
        json: Any | None = None,
        params: Any | None = None,
        proxies: dict[str, str] | None = None,
        timeout: int
        | float
        | tuple[int | float | None, int | float | None]
        | None = None,
        access_token: str | None = None
    ):
        if access_token is None or is_token_expired(access_token):
            access_token = self.refresh_token(refresh_token)["token"]

        return self.proxy(
            access_token,
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

    if FASTAPI:

        def get_router(self, prefix: str = "/api/auth"):
            from fastapi import APIRouter

            router = APIRouter(prefix=prefix)

            @router.post("")
            def api_post_auth(code: str, response: Response):
                res = self.exchange_code(code)
                response.set_cookie("itd_oauth_refresh", res["refresh_token"])
                return {"token": res["access_token"]}

            return router

        def dependency(self, authorization: str = Header()):
            try:
                return decode_jwt_payload(authorization.replace("Bearer ", ""))
            except Exception:
                raise HTTPException(detail="invalid access token", status_code=400)

    else:

        def get_router(self, prefix: str = "/api/auth"):
            raise ImportError(
                "fastapi is required for client.router. Install via: uv add itd-oauth-sdk[fastapi]"
            )

        def dependency(self, access_token: Any = None):
            raise ImportError(
                "fastapi is required for client.dependency. Install via: uv add itd-oauth-sdk[fastapi]"
            )
