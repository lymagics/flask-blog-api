from apiflask import fields, Schema
from marshmallow import validates, ValidationError
from marshmallow.validate import Length

from .auth import token_auth
from .models import User


class UserSchema(Schema):
    """Marshmallow schema to represent 'user'."""
    user_id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=Length(min=3, max=64))
    email = fields.Email(required=True, load_only=True)
    password = fields.String(required=True, load_only=True)
    about_me = fields.String(validate=Length(max=256))
    last_seen = fields.DateTime(dump_only=True)
    member_since = fields.DateTime(dump_only=True)

    @validates("username")
    def validate_username(self, value: str):
        """Validate username for being unique."""
        user = User.query.filter_by(username=value).first()
        if user is not None and user != token_auth.current_user:
            raise ValidationError("Username already in use")

    @validates("email")
    def validate_email(self, value: str):
        """Validate email for being unique."""
        user = User.query.filter_by(email=value).first()
        if user is not None and user != token_auth.current_user:
            raise ValidationError("Email already in use")


class UpdateUserSchema(UserSchema):
    """Marshmallow schema to represent update for 'user'."""
    old_password = fields.String(load_only=True)


class TokenSchema(Schema):
    """Marshmallow schema to represent 'token'."""
    access_token = fields.String(required=True, validate=Length(max=64))
    refresh_token = fields.String(validate=Length(max=64))


class PostSchema(Schema):
    """Marshmallow schema to represent 'post'."""
    post_id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=Length(max=50))
    content = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)


class PostOutSchema(PostSchema):
    """Marshmallow schema to represent 'post' output."""
    author = fields.Nested(UserSchema)


class PaginationQuerySchema(Schema):
    """Marshmallow schema to represent 'pagination' in query."""
    limit = fields.Integer(load_default=10)
    offset = fields.Integer(load_default=0)


class PaginationSchema(Schema):
    """Marshmallow schema to represent 'pagination'."""
    pagination = fields.Nested(PaginationQuerySchema)


class UserPaginationSchema(PaginationSchema):
    """Marshmallow schema to represent paginated 'user'."""
    users = fields.List(fields.Nested(UserSchema))


class PostPaginationSchema(PaginationSchema):
    """Marshmallow schema to represent paginated 'post'."""
    posts = fields.List(fields.Nested(PostOutSchema))
