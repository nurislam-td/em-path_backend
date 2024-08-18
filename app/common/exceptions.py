from email import message_from_string

from fastapi import status


class AppException(Exception):
    status_code = 500
    message = "Server error"
    detail = []

    def __init__(self, detail: dict | None = None):
        self.detail = [] if detail is None else detail


class UserAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    message = "User already exist"


class UserNotExistsException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "User not found"


class IncorrectCredentialsExceptions(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Incorrect user credentials"


class InvalidToken(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid token"


class IncorrectVerificationCode(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Incorrect verification code"


class Unauthorized(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Not authenticated"
