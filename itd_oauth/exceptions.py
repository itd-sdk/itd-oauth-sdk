class InvalidCodeError(Exception):
    def __str__(self):
        return "Invalid code"


class InvalidRefreshTokenError(Exception):
    def __str__(self):
        return "Invalid refresh token"


class SessionRevokedError(Exception):
    def __str__(self):
        return "Session revoked (logged out)"
