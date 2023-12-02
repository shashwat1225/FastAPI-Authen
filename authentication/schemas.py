from typing import Optional

from pydantic import BaseModel


class UserRegisterRequestModel(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str
    re_password: str


class UserRegisterResponseModel(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None


class UserLoginRequestModel(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str


class UserLoginResponseModel(BaseModel):
    access: str
    refresh: str


class UserRefreshTokenRequestModel(BaseModel):
    refresh: str


class UserRefreshTokenResponseModel(BaseModel):
    access: str


class UpdateInfoRequestModel(BaseModel):
    old_password: str
    new_password: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None


class UpdateInfoResponseModel(BaseModel):
    new_password: str
    new_email: str


class ForgotPasswordRequestModel(BaseModel):
    email: str


class ResetPasswordRequestModel(BaseModel):
    password: str
    re_password: str


class ResendEmailActivationRequestModel(BaseModel):
    email: str


class ResendPhoneActivationRequestModel(BaseModel):
    phone_number: str


class BaseMessage(BaseModel):
    message: str
    detail: str