class DetailException(Exception):
    """
    Base exception for services to return a detail message.
    The central handler will catch this and return a 400 Bad Request.
    """
    def __init__(self, detail: str):
        self.detail = detail

class NotFoundException(DetailException):
    """
    Base exception for a 404 Not Found response.
    """
    pass

class UserNotFoundException(NotFoundException):
    """Raised when a user is not found in the database."""
    def __init__(self, detail: str = "User not found."):
        super().__init__(detail)

class ConnectionNotFoundException(NotFoundException):
    """Raised when a family connection is not found in the database."""
    def __init__(self, detail: str = "Connection not found."):
        super().__init__(detail)