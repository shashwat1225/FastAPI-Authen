import re
from datetime import datetime, timedelta
from typing import Union

from decouple import config
from fastapi import FastAPI, Depends
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException

from authentication.auth_utils import (AuthHandler,
                                       send_email,
                                       )
from authentication.error_responses import (UnIdenticalPasswordsException,
                                            DataBaseIntegrityException,
                                            ExpiredActivationTokenException,
                                            InvalidUserException,
                                            InvalidActivationTokenException,
                                            AlreadyActiveUserException,
                                            ActivationEmailLimitException,
                                            NewPasswordException,
                                            ResetPasswordEmailLimitException,
                                            InvalidEmailException,
                                            ExpiredResetPasswordTokenException,
                                            InvalidResetPasswordTokenException,
                                            InvalidPhoneNumberException,
                                            ActivationTextLimitException, UserExistsException,
                                            IncompleteFormException, )
from authentication.schemas import (UserRegisterRequestModel,
                                    UserRegisterResponseModel,
                                    ResendEmailActivationRequestModel,
                                    ResetPasswordRequestModel,
                                    ResendPhoneActivationRequestModel, UserLoginRequestModel,
                                    UserLoginResponseModel, UserRefreshTokenRequestModel, UserRefreshTokenResponseModel,
                                    UpdateInfoRequestModel, UpdateInfoResponseModel, BaseMessage,
                                    )
from sql_app.crud import send_otp, create_model, send_activation_email, get_email_activation_request_by_token, \
    get_user_by_id, get_phone_activation_request_by_otp, send_forgot_password_email
from sql_app.models import (User,
                            EmailActivationRequest,
                            PhoneActivationRequest)
from .error_responses import InvalidUsernameOrPasswordException, WrongOldPasswordException
from .messages import Messages

auth_handler = AuthHandler(algorithm=config('JWT_ALGORITHM'))


class AuthRoutes:
    user_register = '/users'
    user_email_activation = '/users/email-activation/{token}'
    user_phone_activation = '/users/phone-activation/{otp}'
    user_resend_email_activation = '/users/resend-email-activation'
    user_resend_phone_activation = '/users/resend-phone-activation'
    user_login = '/users/login'
    user_refresh_token = '/users/refresh-token'
    user_update_info = '/users/update-info'
    user_forgot_password = '/users/forgot-password'
    user_reset_password = '/users/reset-password/{token}'


def auth_api(app: FastAPI, db: Session) -> None:
    @app.post(AuthRoutes.user_register, response_model=UserRegisterResponseModel)
    async def register(
            request: UserRegisterRequestModel,
    ) -> UserRegisterResponseModel:

        if request.password != request.re_password:
            raise UnIdenticalPasswordsException()
        hashed_password = auth_handler.get_password_hash(request.password)

        if request.phone_number or request.email:
            if request.phone_number and (not request.phone_number.startswith('09')
                                         or len(request.phone_number) != 11):
                raise InvalidPhoneNumberException()
            if request.email and not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                                                  request.email):
                raise InvalidEmailException()

            user = User(password=hashed_password,
                        phone_number=request.phone_number,
                        email=request.email)
            if db.query(User).filter(or_(User.phone_number == request.phone_number,
                                         User.email == request.email)).first():
                raise UserExistsException()
            user = create_model(db, user)
            if request.phone_number:
                send_otp(db, user.id, user.phone_number)
            else:
                send_activation_email(db, user.id, user.email)
            return UserRegisterResponseModel(phone_number=user.phone_number, email=user.email)
        raise IncompleteFormException()
    @app.post(AuthRoutes.user_email_activation, response_model=BaseMessage)
    def email_account_activation(token: str) -> BaseMessage:
        activation_request = get_email_activation_request_by_token(db, token)
        if activation_request:
            email_activation_exp_minutes = int(config('EMAIL_ACTIVATION_EXP_MINUTES'))
            if (activation_request.date_created
                    <
                    datetime.utcnow() - timedelta(minutes=email_activation_exp_minutes)):
                raise ExpiredActivationTokenException()

            user = get_user_by_id(db, activation_request.user)
            if not user:
                raise InvalidUserException()
            user.email_verified_at = datetime.utcnow()
            user.is_active = True

            db.query(EmailActivationRequest).filter_by(user=user.id).delete()
            db.commit()
            return BaseMessage(
                message=Messages.EMAIL_ACTIVATED.name,
                detail=Messages.EMAIL_ACTIVATED.value
            )
        raise InvalidActivationTokenException()

    @app.post(AuthRoutes.user_phone_activation, response_model=BaseMessage)
    def phone_activation(otp: int) -> BaseMessage:
        activation_request = get_phone_activation_request_by_otp(db, otp)
        if activation_request:
            phone_activation_exp_minutes = int(config('PHONE_ACTIVATION_EXP_MINUTES'))
            if (activation_request.date_created
                    <
                    datetime.utcnow() - timedelta(minutes=phone_activation_exp_minutes)):
                db.delete(activation_request)
                db.commit()
                raise ExpiredActivationTokenException()
            user: User = get_user_by_id(db, activation_request.user)
            if not user:
                raise InvalidUserException()
            user.phone_verified_at = datetime.utcnow()
            user.is_active = True
            db.query(PhoneActivationRequest).filter_by(user=user.id).delete()
            db.commit()
            return BaseMessage(
                message=Messages.PHONE_ACTIVATED.name,
                detail=Messages.PHONE_ACTIVATED.value
            )
        raise InvalidActivationTokenException()

    @app.post(AuthRoutes.user_resend_email_activation, response_model=BaseMessage)
    async def resend_activation_email(request: ResendEmailActivationRequestModel) -> BaseMessage:
        user: User = db.query(User).filter_by(email=request.email).first()
        if not user:
            raise InvalidUserException()
        if user.email_verified_at:
            raise AlreadyActiveUserException()
        email_limit = int(config('EMAIL_ACTIVATION_LIMIT'))
        email_activation_exp_minutes = int(config('EMAIL_ACTIVATION_EXP_MINUTES'))
        emails = db.query(EmailActivationRequest) \
            .filter(EmailActivationRequest.date_created
                    >
                    datetime.utcnow() - timedelta(hours=email_activation_exp_minutes)). \
            count()
        if emails > email_limit:
            raise ActivationEmailLimitException()
        send_activation_email(db, user.id, user.email)
        return BaseMessage(
            message=Messages.EMAIL_ACTIVATION_RESEND.name,
            detail=Messages.EMAIL_ACTIVATION_RESEND.value
        )

    @app.post(AuthRoutes.user_resend_phone_activation, response_model=BaseMessage)
    async def resend_activation_sms(request: ResendPhoneActivationRequestModel) -> BaseMessage:
        if not request.phone_number.startswith('09') or len(request.phone_number) != 11:
            raise InvalidPhoneNumberException()
        user: User = db.query(User).filter_by(phone_number=request.phone_number).first()
        if not user:
            raise InvalidUserException()
        if user.phone_verified_at:
            raise AlreadyActiveUserException()
        phone_limit = int(config('PHONE_ACTIVATION_LIMIT'))
        phone_activation_exp_minutes = int(config('PHONE_ACTIVATION_EXP_MINUTES'))
        sent_sms = db.query(PhoneActivationRequest) \
            .filter(
            PhoneActivationRequest.date_created > datetime.utcnow() - timedelta(hours=phone_activation_exp_minutes)) \
            .count()
        if sent_sms > phone_limit:
            raise ActivationTextLimitException()
        send_otp(db, user.id, user.phone_number)
        return BaseMessage(
            message=Messages.PHONE_ACTIVATION_RESEND.name,
            detail=Messages.PHONE_ACTIVATION_RESEND.value
        )

    @app.post(AuthRoutes.user_login, response_model=UserLoginResponseModel)
    def login(request: UserLoginRequestModel) -> UserLoginResponseModel:
        user: User = db.query(User).filter(or_(User.email == request.email, User.phone_number == request.phone_number)). \
            first()
        if not user:
            raise InvalidUserException()
        if (user and user.is_active
                and auth_handler.verify_password(plain_password=request.password,
                                                 hashed_password=user.password)):
            acc_token = auth_handler.encode_token(user_id=user.id, access_token=True)
            ref_token = auth_handler.encode_token(user_id=user.id, access_token=False)
            return UserLoginResponseModel(access=acc_token, refresh=ref_token)
        raise InvalidUsernameOrPasswordException()

    @app.post(AuthRoutes.user_refresh_token, response_model=UserRegisterResponseModel)
    def refresh_token(request: UserRefreshTokenRequestModel) -> Union[HTTPException, UserRefreshTokenResponseModel]:
        user_id = auth_handler.decode_token(token=request.refresh)
        new_acc_token = auth_handler.encode_token(user_id=user_id, access_token=True)
        return UserRefreshTokenResponseModel(accessToken=new_acc_token)

    @app.patch(AuthRoutes.user_update_info, response_model=UpdateInfoResponseModel)
    def update_info(request: UpdateInfoRequestModel,
                    username=Depends(auth_handler.auth_wrapper)) -> UpdateInfoResponseModel:
        user: User = db.query(User).filter_by(username=username).first()
        if user and auth_handler.verify_password(plain_password=request.old_password,
                                                 hashed_password=user.password):

            if request.email:
                user.email = request.email
                user.email_verified_at = None
            if request.phone_number:
                user.phone_number = request.phone_number
                user.phone_verified_at = None
            if request.new_password:
                if auth_handler.verify_password(plain_password=request.new_password, hashed_password=user.password):
                    raise NewPasswordException()
                user.password = auth_handler.get_password_hash(request.new_password)
            try:
                db.commit()
            except IntegrityError as e:
                db.rollback()
                raise DataBaseIntegrityException(message=e.orig.args[0])
            return UpdateInfoResponseModel(new_username=user.username,
                                           new_password=request.new_password,
                                           new_email=user.email)
        raise WrongOldPasswordException()

    @app.put(AuthRoutes.user_update_info, response_model=UpdateInfoResponseModel)
    def update_info(request: UpdateInfoRequestModel,
                    username=Depends(auth_handler.auth_wrapper)) -> UpdateInfoResponseModel:
        user: User = db.query(User).filter_by(username=username).first()
        if user and auth_handler.verify_password(plain_password=request.old_password,
                                                 hashed_password=user.password):
            if (not request.phone_number and not request.email) or not request.new_password:
                raise IncompleteFormException()
            if auth_handler.verify_password(plain_password=request.new_password, hashed_password=user.password):
                raise NewPasswordException()
            if request.email and not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                                                  request.email):
                raise InvalidEmailException()
            user.email = request.email
            user.phone_number = request.phone_number
            if request.email != user.email:
                user.email_verified_at = None
            if request.phone_number != user.phone_number:
                user.phone_verified_at = None
            user.password = auth_handler.get_password_hash(request.new_password)
            try:
                db.commit()
            except IntegrityError as e:
                db.rollback()
                raise DataBaseIntegrityException(message=e.orig.args[0])
            return UpdateInfoResponseModel(new_username=user.username,
                                           new_password=request.new_password,
                                           new_email=user.email)
        raise WrongOldPasswordException()

    @app.post(AuthRoutes.user_forgot_password, response_model=BaseMessage)
    async def forgot_password(request: ResendEmailActivationRequestModel) -> BaseMessage:
        email = request.email
        user: User = db.query(User).filter_by(email=email).first()
        if user:
            email_limit = int(config('EMAIL_ACTIVATION_LIMIT'))
            email_activation_exp_minutes = int(config('EMAIL_ACTIVATION_EXP_MINUTES'))
            emails = db.query(EmailActivationRequest) \
                .filter(EmailActivationRequest.date_created
                        >
                        datetime.utcnow() - timedelta(minutes=email_activation_exp_minutes)). \
                count()
            if emails > email_limit:
                raise ResetPasswordEmailLimitException()
            send_forgot_password_email(db, email=email, user_id=user.id)
            return BaseMessage(message=Messages.EMAIL_SENT.name, detail=Messages.EMAIL_SENT.value)
        raise InvalidEmailException()

    @app.post(AuthRoutes.user_reset_password, response_model=BaseMessage)
    async def reset_password(token: str, request: ResetPasswordRequestModel) -> BaseMessage:
        reset_password_request = get_email_activation_request_by_token(db, token)
        if reset_password_request:
            email_activation_exp_minutes = int(config('EMAIL_ACTIVATION_EXP_MINUTES'))
            if (reset_password_request.date_created
                    <
                    datetime.utcnow() - timedelta(
                        minutes=email_activation_exp_minutes)):
                db.delete(reset_password_request)
                db.commit()
                raise ExpiredResetPasswordTokenException()
            user: User = db.query(User).filter_by(id=reset_password_request.user).first()
            if user:
                if request.password != request.re_password:
                    raise UnIdenticalPasswordsException()
                if auth_handler.verify_password(plain_password=request.password, hashed_password=user.password):
                    raise NewPasswordException()
                user.password = auth_handler.get_password_hash(password=request.password)
                db.commit()
                await send_email(subject='password reset successful',
                                 recipients=[user.email],
                                 body='your password has been changed successfully')
                db.query(EmailActivationRequest).filter_by(user_email=user.email).delete()
                db.commit()
                return BaseMessage(message=Messages.PASSWORD_CHANGED.name, detail=Messages.PASSWORD_CHANGED.value)
        raise InvalidResetPasswordTokenException()