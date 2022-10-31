from apiflask import abort, HTTPBasicAuth, HTTPTokenAuth
from .models import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    """Verify user password."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(401, "Unauthorized")
    if user.verify_password(password):
        return user


@token_auth.verify_token
def verify_token(token):
    """Verify access token."""
    return User.verify_access_token(token)
    