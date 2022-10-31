from functools import wraps

from apiflask import abort, APIBlueprint

from .. import schemas
from ..auth import token_auth
from ..models import db, User

users = APIBlueprint("users", __name__)


def paginated_users(f):
    """If you decorate view with this, it will return paginated users response."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        args = list(args)
        pagination = args.pop(-1)
        res = f(*args, **kwargs)
        users = res.limit(pagination["limit"]).offset(pagination["offset"]).all()
        return {"users": users, "pagination": pagination}
    return wrapper


@users.post("/users")
@users.input(schemas.UserSchema)
@users.output(schemas.UserSchema, status_code=201)
@users.doc(summary="Create new user.", description="Create new user.")
def new(data: dict):
    """Create new user."""
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user


@users.get("/users")
@users.input(schemas.PaginationQuerySchema, location="query")
@users.output(schemas.UserPaginationSchema)
@users.doc(summary="Retrieve all users.", description="Retrieve all users with pagination.")
@paginated_users
def all():
    """Retrieve all users."""
    return User.query


@users.get("/users/<int:user_id>")
@users.output(schemas.UserSchema)
@users.doc(summary="Retrieve user by id.", description="Retrieve user by id.")
def get(user_id: int):
    """Retrieve user by id."""
    user = User.query.filter_by(user_id=user_id).first()
    if user is None:
        abort(404, "User not found")
    return user 


@users.get("/users/<username>")
@users.output(schemas.UserSchema)
@users.doc(summary="Retrieve user by username.", description="Retrieve user by username.")
def get_by_username(username: str):
    """Retrieve user by username."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404, "User not found")
    return user


@users.get("/me")
@users.auth_required(token_auth)
@users.output(schemas.UserSchema)
@users.doc(summary="Retrieve authenticated user.", description="Retrieve authenticated user.")
def me():
    """Retrieve authenticated user."""
    return token_auth.current_user


@users.put("/me")
@users.auth_required(token_auth)
@users.input(schemas.UpdateUserSchema(partial=True))
@users.output(schemas.UserSchema)
@users.doc(summary="Update user information.", description="Update user information.")
def put(data: dict):
    """Update user information."""
    user = token_auth.current_user
    if "password" in data and ("old_password" not in data or
                                not user.verify_password(data["old_password"])):
        abort(403)
    user.update(data)
    db.session.commit()
    return user
