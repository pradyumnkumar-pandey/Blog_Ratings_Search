from datetime import datetime, timedelta
import jwt
from django.conf import settings


def get_access_token(user):
    access_token_payload = {
        'user_id': user.id,
        'token_type': 'access',
        'exp': datetime.utcnow()+timedelta(minutes=250),
        'iat': datetime.utcnow(),
        'jti': f'ea0f38b5789242459151791f835f9ba5{datetime.utcnow()}', }

    access_token = jwt.encode(access_token_payload,settings.SECRET_KEY, algorithm='HS256')
    return access_token


def get_refresh_token(user):
    refresh_token_payload = {
        'user_id': user.id,
        'token_type': 'refresh',
        'exp': datetime.utcnow()+timedelta(minutes=45),
        'iat': datetime.utcnow(),
        'jti': f'ea0f38b5789242459151791f835f9ba5{datetime.utcnow()}', }

    refresh_token = jwt.encode(
        refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')
    return refresh_token
