import hashlib
import logging
import string
import random
import settings
import base64

from lib.itsdangerous import TimestampSigner
from lib.itsdangerous import BadSignature

from base import mail as base_mail

ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits


def generate_salt(size=64):
    random.seed()
    return ''.join([random.choice(ALPHABET) for i in range(0, size)])


def encode_password(raw_password, salt=None):

    if not salt:
        salt = generate_salt()

    h = hashlib.new('sha512')
    h.update(raw_password)
    h.update(salt)

    return h.hexdigest(), salt


def check_password(raw_password, email):
    from auth import models as auth_models
    user = auth_models.WTUser.all().filter('email =', email).fetch(1)

    if len(user):
        user = user[0]
        response_hash, salt = encode_password(raw_password, user.salt)
        return response_hash == user.password

    else:
        return False


def generate_signed_token(input):
    signer = TimestampSigner(settings.SECRET_KEY)
    signed_string = signer.sign(input)
    return base64.b64encode(signed_string)


def validate_token(token):
    signer = TimestampSigner(settings.SECRET_KEY)
    decoded_string = base64.b64decode(token)
    try:
        output = signer.unsign(decoded_string, settings.TOKEN_SIGNING_TIMELIMIT)
    except BadSignature, e:
        return False

    return output


def send_reset_email(server, user):
    token = generate_signed_token(user.email)
    link = '%s/auth/reset_password?token=%s' % (server, token)
    body = base_mail.generate_email_body('email/auth/reset_email.html', {'username': 'username', 'reset_link': link})
    base_mail.send_email(user.email, "BoxTrackr Password Reset", body)
    return True
