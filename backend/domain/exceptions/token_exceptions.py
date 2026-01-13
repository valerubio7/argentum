"""Token-specific domain exceptions."""


class TokenDomainError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidTokenError(TokenDomainError):
    def __init__(self, reason: str = "Token is invalid"):
        self.reason = reason
        super().__init__(reason)


class ExpiredTokenError(TokenDomainError):
    def __init__(self):
        super().__init__("Token has expired")


class InvalidTokenFormatError(TokenDomainError):
    def __init__(self, details: str = "Invalid token format"):
        self.details = details
        super().__init__(details)
