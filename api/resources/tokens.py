from apiflask import abort, APIBlueprint
from flask import current_app, url_for, request
from werkzeug.http import dump_cookie

from ..auth import basic_auth
from .. import schemas
from ..models import db, Token, User

tokens = APIBlueprint("tokens", __name__)


def token_response(token: Token) -> dict:
    """Construct valid token response."""
    headers = {}
    samesite = "strict"
    if current_app.config["USE_CORS"]:
        samesite = "none" if not current_app.debug else "lax"
    if current_app.config["REFRESH_TOKEN_IN_COOKIE"]:
        headers["Set-Cookie"] = dump_cookie(
            "refresh_token", token.refresh_token,
            path=url_for("tokens.new"), httponly=True,
            secure= not current_app.debug, samesite=samesite
        ) 
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token
            if current_app.config["REFRESH_TOKEN_IN_BODY"] else None
    }, 201, headers


@tokens.post("/tokens")
@tokens.auth_required(basic_auth)
@tokens.output(schemas.TokenSchema)
@tokens.doc(summary="Create new access token.", description="Create new access token.")
def new():
    """Create new access token."""
    user = basic_auth.current_user
    token = user.generate_access_token()
    Token.clean()
    db.session.commit()
    return token_response(token) 


@tokens.put("/tokens")
@tokens.input(schemas.TokenSchema)
@tokens.output(schemas.TokenSchema)
@tokens.doc(summary="Refresh access token.", description="Refresh access token.")
def refresh(data: dict):
    """Refresh access token."""
    access_token = data["access_token"]
    refresh_token = data.get("refresh_token") or request.cookies.get("refresh_token")
    if not refresh_token:
        abort(400)
    
    token = User.verify_refresh_token(refresh_token, access_token)
    if token is None:
        abort(401)
    token.expire()
    new_token = token.user.generate_access_token()
    db.session.add_all([token, new_token])
    db.session.commit()
    return token_response(new_token)


@tokens.delete("/tokens")
@tokens.input(schemas.TokenSchema)
@tokens.output(schemas.TokenSchema, status_code=204)
@tokens.doc(summary="Revoke access token.", description="Revoke access token.")
def revoke(data: dict):
    """Revoke access token."""
    token = Token.query.filter_by(access_token=data["access_token"]).first()
    if token is None:
        abort(401)
    token.expire()
    db.session.commit()
    return {}
