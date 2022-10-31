import secrets
from datetime import datetime, timedelta

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from . import db 


class Updatable:
    """Class for update logic."""
    def update(self, data: dict):
        for attr, value in data.items():
            setattr(self, attr, value)


# Followers many-to-many table.
followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("users.user_id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("users.user_id"))
)


class Token(db.Model):
    """SQLAlchemy model to represent 'tokens' table."""
    __tablename__ = "tokens"

    token_id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(64), nullable=False, index=True)
    access_expiration = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(64), nullable=False, index=True)
    refresh_expiration = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    def generate(self):
        """Generate access and refresh tokens."""
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() + \
            timedelta(minutes=current_app.config["ACCESS_TOKEN_EXPIRE_MINUTES"])
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = datetime.utcnow() + \
            timedelta(days=current_app.config["REFRESH_TOKEN_EXPIRE_DAYS"])

    def expire(self):
        """Expire access and refresh tokens."""
        self.access_expiration = datetime.utcnow()
        self.refresh_expiration = datetime.utcnow()

    @staticmethod
    def clean():
        """Remove all tokens from database if they are expired for more than one day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        Token.query.filter(Token.refresh_expiration < yesterday).delete()


class Post(Updatable, db.Model):
    """SQLAlchemy model to represent 'posts' table."""
    __tablename__ = "posts"

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    def __repr__(self):
        return f"<Post {self.title}>"


class User(Updatable, db.Model):
    """SQLAlchemy model to represent 'users' table."""
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(256))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)

    tokens = db.relationship("Token", backref="user", cascade="all,delete", lazy="dynamic")
    posts = db.relationship("Post", backref="author", cascade="all,delete", lazy="dynamic")

    followed = db.relationship(
        "User", secondary=followers,
        primaryjoin=(followers.c.follower_id == user_id),
        secondaryjoin=(followers.c.followed_id == user_id),
        backref=db.backref("followers", lazy="dynamic"), lazy="dynamic")

    @property
    def password(self):
        """Password getter."""
        raise AttributeError("Can't read user password.")

    @password.setter
    def password(self, password: str):
        """Password setter."""
        self.password_hash = generate_password_hash(password)

    def ping(self):
        """Update user last seen time."""
        self.last_seen = datetime.utcnow()

    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def generate_access_token(self):
        """Generate access and refresh token pair."""
        token = Token(user=self)
        token.generate()
        db.session.add(token)
        return token

    @staticmethod
    def verify_access_token(access_token):
        """Verify access token and return user instance."""
        token = Token.query.filter_by(access_token=access_token).first()
        if token and token.access_expiration > datetime.utcnow():
            token.user.ping()
            db.session.commit()
            return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token):
        """Verify refresh token and return token instance."""
        token = Token.query.filter_by(refresh_token=refresh_token).first()
        if token:
            if token.refresh_expiration > datetime.utcnow():
                return token

    def is_following(self, user):
        """Check if current user follows user."""
        return self in user.followers

    def is_followed_by(self, user):
        """Check if current user is followed by user."""
        return self in user.followed

    def follow(self, user):
        """Follow user."""
        if not self.is_following(user):
            user.followers.append(self)

    def unfollow(self, user):
        """Unfollow user."""
        if self.is_following(user):
            user.followers.remove(self)

    def select_following(self):
        """Select users current user follows."""
        return self.followed

    def select_followers(self):
        """Select current user followers."""
        return self.followers

    def __repr__(self):
        return f"<User {self.username}>"
        