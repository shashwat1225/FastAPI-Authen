from datetime import datetime, timedelta
from typing import List

import jwt
from decouple import config
from fastapi import  Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_mail import FastMail, MessageSchema
from passlib.context import CryptContext
from authentication.error_responses import InvalidTokenException, ExpiredSignatureException
from configuration.email_config import email_conf
from configuration.private_key_config import private_key


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, algorithm: str):
        self.algorithm = algorithm
        with open("../private-key.pem", "rb") as key_file:
            self.private_key = key_file.read()
    # todo : add init for JWT Auth
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id, access_token: bool):
        if access_token:
            t_delta = timedelta(days=int(config('JWT_ACCESS_EXP_HOURS')))
            token_type = 'access'
        else:
            t_delta = timedelta(days=int(config('JWT_REFRESH_EXP_HOURS')))
            token_type = 'refresh'
        payload = {
            'exp': datetime.utcnow() + t_delta,
            'iat': datetime.utcnow(),
            'type': token_type,
            'user_id': user_id
        }
        return jwt.encode(
            payload=payload,
            key=self.private_key,
            algorithm=self.algorithm
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.private_key, algorithms=self.algorithm)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise ExpiredSignatureException()
        except jwt.InvalidTokenError:
            raise InvalidTokenException()

    def token_is_refresh(self, token) -> bool:
        payload = jwt.decode(token, self.private_key, algorithms=self.algorithm)
        if payload['type'] == 'refresh':
            return True
        return False

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        if self.token_is_refresh(auth.credentials):
            raise InvalidTokenException()
        return self.decode_token(auth.credentials)


async def send_email(subject: str, recipients: List[str], body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,

    )
    fm = FastMail(email_conf)
    await fm.send_message(message)