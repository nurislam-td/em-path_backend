from fastapi import HTTPException, status


class AppException(HTTPException):
    status_code = 500
    detail = "Server error"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User already exist"


class IncorrectCredentialsExceptions(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Incorrect user credentials"


class InvalidToken(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid token"


class IncorrectVerificationCode(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Incorrect verification code"
