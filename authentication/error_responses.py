from fastapi import Request
from starlette import status
from fastapi import FastAPI
from fastapi.responses import JSONResponse


class Codes:
    UnIdenticalPasswords = 1
    DataBaseIntegrity = 2
    ExpiredActivationToken = 3
    InvalidUser = 4
    InvalidActivationToken = 5
    AlreadyActiveUser = 6
    ActivationEmailLimit = 7
    InvalidUsernameOrPassword = 8
    NewPassword = 9
    WrongOldPassword = 10
    IncompleteForm = 11
    ResetPasswordEmailLimit = 12
    InvalidEmail = 13
    ExpiredResetPasswordToken = 14
    InvalidResetPasswordToken = 15
    InvalidToken = 16
    ExpiredSignature = 17
    InvalidPhoneNumber = 18
    NoPhoneAndEmail = 19
    ActivationTextLimit = 20
    AlreadyExists = 21
    InternalServerError = 22


class BaseMessage:
    def __init__(self, code, message, status_code):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.response = JSONResponse(status_code=self.status_code,
                                     content={
                                         'message': self.message,
                                         'error_code': self.code
                                     })


class UnIdenticalPasswordsException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'passwords do not match'
    error_code = Codes.UnIdenticalPasswords


class DataBaseIntegrityException(Exception):
    def __init__(self, message: str):
        self.message = message

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = Codes.DataBaseIntegrity

class InternalServerErrorException(Exception):
    def __init__(self, message: str):
        self.message = message

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = Codes.InternalServerError

class ExpiredActivationTokenException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'activation request token has been expired'
    error_code = Codes.ExpiredActivationToken


class ExpiredResetPasswordTokenException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'password reset request token has been expired'
    error_code = Codes.ExpiredResetPasswordToken


class InvalidUserException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'invalid user'
    error_code = Codes.InvalidUser


class InvalidActivationTokenException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'invalid activation token'
    error_code = Codes.InvalidActivationToken


class AlreadyActiveUserException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'user is already active'
    error_code = Codes.AlreadyActiveUser


class ActivationEmailLimitException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'activation email request rate limit reached please be patient'
    error_code = Codes.ActivationEmailLimit


class ActivationTextLimitException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'activation text request rate limit reached please be patient'
    error_code = Codes.ActivationTextLimit


class ResetPasswordEmailLimitException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'password reset email request rate limit reached please be patient'
    error_code = Codes.ResetPasswordEmailLimit


class InvalidUsernameOrPasswordException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'invalid credentials'
    error_code = Codes.InvalidUsernameOrPassword


class NewPasswordException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'new password can not be the same as the old password!'
    error_code = Codes.NewPassword


class WrongOldPasswordException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'old password was not entered correctly'
    error_code = Codes.WrongOldPassword


class IncompleteFormException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'all fields required'
    error_code = Codes.IncompleteForm


class NoPhoneAndEmailException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'make sure to enter your phone number and or email!'
    error_code = Codes.NoPhoneAndEmail


class InvalidEmailException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'invalid email address'
    error_code = Codes.InvalidEmail


class InvalidResetPasswordTokenException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'invalid password reset token'
    error_code = Codes.InvalidResetPasswordToken


class InvalidPhoneNumberException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'invalid phone number'
    error_code = Codes.InvalidPhoneNumber


class InvalidTokenException(Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = 'invalid token'
    error_code = Codes.InvalidToken


class ExpiredSignatureException(Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = 'Signature has expired'
    error_code = Codes.ExpiredSignature


class UserExistsException(Exception):
    status_code = status.HTTP_409_CONFLICT
    message = 'Conflict: already exists'
    error_code = Codes.AlreadyExists


def handlers(app: FastAPI) -> None:
    @app.exception_handler(UnIdenticalPasswordsException)
    async def unidentical_passwords_handler(request: Request, exc: UnIdenticalPasswordsException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(DataBaseIntegrityException)
    async def unidentical_passwords_handler(request: Request, exc: DataBaseIntegrityException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(ExpiredActivationTokenException)
    async def unidentical_passwords_handler(request: Request, exc: ExpiredActivationTokenException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(InvalidUserException)
    async def unidentical_passwords_handler(request: Request, exc: InvalidUserException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(InvalidActivationTokenException)
    async def unidentical_passwords_handler(request: Request, exc: InvalidActivationTokenException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(AlreadyActiveUserException)
    async def unidentical_passwords_handler(request: Request, exc: AlreadyActiveUserException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(ActivationEmailLimitException)
    async def unidentical_passwords_handler(request: Request, exc: ActivationEmailLimitException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(InvalidUsernameOrPasswordException)
    async def unidentical_passwords_handler(request: Request, exc: InvalidUsernameOrPasswordException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(NewPasswordException)
    async def unidentical_passwords_handler(request: Request, exc: NewPasswordException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(WrongOldPasswordException)
    async def unidentical_passwords_handler(request: Request, exc: WrongOldPasswordException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(IncompleteFormException)
    async def unidentical_passwords_handler(request: Request, exc: IncompleteFormException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(ResetPasswordEmailLimitException)
    async def unidentical_passwords_handler(request: Request, exc: ResetPasswordEmailLimitException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(InvalidEmailException)
    async def unidentical_passwords_handler(request: Request, exc: InvalidEmailException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(ExpiredResetPasswordTokenException)
    async def unidentical_passwords_handler(request: Request, exc: ExpiredResetPasswordTokenException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(InvalidResetPasswordTokenException)
    async def unidentical_passwords_handler(request: Request, exc: InvalidResetPasswordTokenException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(InvalidTokenException)
    async def unidentical_passwords_handler(request: Request, exc: InvalidTokenException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(ExpiredSignatureException)
    async def unidentical_passwords_handler(request: Request, exc: ExpiredSignatureException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(InvalidPhoneNumberException)
    async def unidentical_passwords_handler(request: Request, exc: InvalidPhoneNumberException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(NoPhoneAndEmailException)
    async def unidentical_passwords_handler(request: Request, exc: NoPhoneAndEmailException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(ActivationTextLimitException)
    async def unidentical_passwords_handler(request: Request, exc: ActivationTextLimitException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response

    @app.exception_handler(UserExistsException)
    async def unidentical_already_exists(request: Request, exc: UserExistsException):
        return BaseMessage(exc.error_code, exc.message, exc.status_code).response


