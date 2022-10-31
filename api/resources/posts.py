from functools import wraps

from apiflask import abort, APIBlueprint

from .. import schemas
from ..auth import token_auth
from ..models import db, Post, User

posts = APIBlueprint("posts", __name__)


def paginated_posts(f):
    """If you decorate view with this, it will return paginated posts response."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        args = list(args)
        pagination = args.pop(-1)
        res = f(*args, **kwargs)
        posts = res.limit(pagination["limit"]).offset(pagination["offset"]).all()
        return {"posts": posts, "pagination": pagination}
    return wrapper


@posts.post("/posts")
@posts.auth_required(token_auth)
@posts.input(schemas.PostSchema)
@posts.output(schemas.PostOutSchema, status_code=201)
@posts.doc(summary="Create new post.", description="Create new post.")
def new(data: dict):
    """Create new post."""
    user = token_auth.current_user
    post = Post(author=user, **data)
    db.session.add(post)
    db.session.commit()
    return post 


@posts.get("/posts")
@posts.input(schemas.PaginationQuerySchema, location="query")
@posts.output(schemas.PostPaginationSchema)
@posts.doc(summary="Retrieve all posts.", description="Retrieve all posts with pagination.")
@paginated_posts
def all():
    """Retrieve all posts."""
    return Post.query


@posts.get("/posts/<int:post_id>")
@posts.output(schemas.PostOutSchema)
@posts.doc(summary="Retrieve post by id.", description="Retrieve post by id.")
def get(post_id: int):
    """Retrieve post by id."""
    post = Post.query.filter_by(post_id=post_id).first()
    if post is None:
        abort(404, "Post not found")
    return post


@posts.get("/users/<int:user_id>/posts")
@posts.input(schemas.PaginationQuerySchema, location="query")
@posts.output(schemas.PostPaginationSchema)
@posts.doc(summary="Retrieve all user posts.", description="Retrieve all user posts with pagination.")
@paginated_posts
def all_user_posts(user_id: int):
    """Retrieve all user posts."""
    user = User.query.filter_by(user_id=user_id).first()
    if user is None:
        abort(404, "User not found")
    return user.posts


@posts.put("/posts/<int:post_id>")
@posts.auth_required(token_auth)
@posts.input(schemas.PostSchema(partial=True))
@posts.output(schemas.PostOutSchema)
@posts.doc(summary="Update post.", description="Update post.")
def put(post_id: int, data: dict):
    """Update post."""
    post = Post.query.filter_by(post_id=post_id).first()
    if post is None:
        abort(404, "Post not found")
    if post.author != token_auth.current_user:
        abort(403, "This is not your post")
    post.update(data)
    db.session.commit()
    return post


@posts.delete("/posts/<int:post_id>")
@posts.auth_required(token_auth)
@posts.output({}, status_code=204)
@posts.doc(summary="Delete post.", description="Delete post.")
def delete(post_id: int):
    """Delete post."""
    post = Post.query.filter_by(post_id=post_id).first()
    if post is None:
        abort(404, "Post not found")
    if post.author != token_auth.current_user:
        abort(403, "This is not your post")
    db.session.delete(post)
    db.session.commit()
    return {}
