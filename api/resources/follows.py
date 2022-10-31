from apiflask import abort, APIBlueprint

from .. import schemas
from ..auth import token_auth
from ..models import db, User
from .users import paginated_users

follows = APIBlueprint("follows", __name__)


@follows.get("/me/following")
@follows.auth_required(token_auth)
@follows.input(schemas.PaginationQuerySchema, location="query")
@follows.output(schemas.UserPaginationSchema)
@follows.doc(summary="Retrieve users the autheticated user is following.", description="Retrieve users the autheticated user is following.")
@paginated_users
def my_followed():
    """Retrieve users the autheticated user is following."""
    user = token_auth.current_user
    return user.select_following()


@follows.get("/me/followers")
@follows.auth_required(token_auth)
@follows.input(schemas.PaginationQuerySchema, location="query")
@follows.output(schemas.UserPaginationSchema)
@follows.doc(summary="Retrieve autheticated user is followers.", description="Retrieve autheticated user is followers.")
@paginated_users
def my_followers():
    """Retrieve autheticated user is followers."""
    user = token_auth.current_user
    return user.select_followers()


@follows.get("/me/following/<int:user_id>")
@follows.auth_required(token_auth)
@follows.output({}, status_code=204)
@follows.doc(summary="Check is user is followed by current user.", description="Check is user is followed by current user.")
def is_following(user_id: int):
    """Check is user is followed by current user."""
    me = token_auth.current_user
    user = User.query.filter_by(user_id=user_id).first()
    if user is None or not me.is_following(user):
        abort(404)
    return {}


@follows.post("/me/following/<user_id>")
@follows.auth_required(token_auth)
@follows.output({}, status_code=204)
@follows.doc(summary="Follow user.", description="Follow user.")
def follow(user_id: int):
    """Follow user."""
    me = token_auth.current_user
    user = User.query.filter_by(user_id=user_id).first()
    if user is None:
        abort(404)
    if me.is_following(user):
        abort(409, "You already follow this user.")
    me.follow(user)
    db.session.commit()
    return {}


@follows.delete("/me/following/<int:user_id>")
@follows.auth_required(token_auth)
@follows.output({}, status_code=204)
@follows.doc(summary="Unfollow user.", description="Unfollow user.")
def unfollow(user_id: int):
    """Unfollow user."""
    me = token_auth.current_user
    user = User.query.filter_by(user_id=user_id).first()
    if user is None:
        abort(404)
    if not me.is_following(user):
        abort(409, "You don't follow this user")
    me.unfollow(user)
    db.session.commit()
    return {}


@follows.get("/users/<int:user_id>/following")
@follows.input(schemas.PaginationQuerySchema, location="query")
@follows.output(schemas.UserPaginationSchema)
@follows.doc(summary="Retrieve the users this user is following.", description="Retrieve the users this user is following")
@paginated_users
def followed(user_id: int):
    """Retrieve the users this user is following."""
    user = User.query.filter_by(user_id=user_id).first()
    if user is None:
        abort(404, "User not found")
    return user.select_following() 


@follows.get("/users/<int:user_id>/followers")
@follows.input(schemas.PaginationQuerySchema, location="query")
@follows.output(schemas.UserPaginationSchema)
@follows.doc(summary="Retrieve user followers.", description="Retrieve user followers.")
@paginated_users
def followers(user_id: int):
    """Retrieve user followers."""
    user = User.query.filter_by(user_id=user_id).first()
    if user is None:
        abort(404, "User not found")
    return user.select_followers()
