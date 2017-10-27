from app import jwt
from ..models import BlacklistToken


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    token = BlacklistToken.query.filter_by(token=jti).first()
    if token:
        return True

    else:
        return False
