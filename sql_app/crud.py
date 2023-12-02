import random
import uuid

from decouple import config
from kavenegar import APIException, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from authentication.auth_utils import send_email
from authentication.error_responses import InternalServerErrorException, DataBaseIntegrityException
from authentication.settings import kavenegarSMSApi
from sql_app.models import PhoneActivationRequest, EmailActivationRequest, User


def create_model(db: Session, model):
    try:
        db.add(model)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise DataBaseIntegrityException(message=e.orig.args[0])
    return model


def send_otp(db: Session, user_id: int, phone_number: str):
    """
      This function sends an OTP to the user's phone number.
    """
    otp = random.randint(10000, 999999)
    model = PhoneActivationRequest(
        user=user_id,
        otp=otp
    )
    model = create_model(db, model)
    try:
        params = {
            'receptor': phone_number,
            'template': config('KAVENEGAR_VERIFICATION_TEMPLATE_NAME'),
            'token': otp,
            'type': 'sms',  # sms vs call
        }
        kavenegarSMSApi.verify_lookup(params)
    except APIException as e:
        return InternalServerErrorException('Error in send_verification_sms')
    except HTTPException as e:
        return InternalServerErrorException('Error in send_verification_sms')
    return model


def send_activation_email(db: Session, user_id: int, email: str):
    """
      This function sends an activation email to the user's email address.
    """
    activation_token = uuid.uuid4().hex
    model = EmailActivationRequest(
        user=user_id,
    )
    model = create_model(db, model)
    activation_link = f'http://127.0.0.1:8000/users/activation/{activation_token}'
    send_email(
        subject='Verify your email address',
        recipients=[email],
        body=f'to activate your account please click on this link {activation_link}',
    )


def send_forgot_password_email(db: Session, user_id: int, email: str):
    """
      This function sends forgot password email to the user's email address.
    """
    activation_token = uuid.uuid4().hex
    model = EmailActivationRequest(
        user=user_id,
    )
    model = create_model(db, model)
    activation_link = f'http://127.0.0.1:8000/users/reset-password/{activation_token}'
    send_email(
        subject='forgot password email address',
        recipients=[email],
        body=f'to change your password click here {activation_link}',
    )


def get_email_activation_request_by_token(db: Session, token: str):
    """
      This function gets an email activation request by token.
    """
    return db.query(EmailActivationRequest).filter_by(token=token).first()


def get_phone_activation_request_by_otp(db: Session, otp: int):
    """
      This function gets a phone activation request by otp.
    """
    return db.query(PhoneActivationRequest).filter_by(otp=otp).first()


def delete_email_activation_request(db: Session, token: str):
    """
      This function deletes an email activation request by token.
    """
    db.query(EmailActivationRequest).filter_by(token=token).delete()
    db.commit()


def get_user_by_id(db: Session, user_id: int):
    """
      This function gets a user by id.
    """
    return db.query(User).filter_by(id=user_id).first()