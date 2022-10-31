import os
from dotenv import load_dotenv

# Base directory path.
base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


def as_bool(val: str) -> bool:
    """Convert any value to bool."""
    if str(val).lower() in ["true", "yes", "1"]:
        return True 
    return False 


class Config:
    """Application config."""
    # Secret key for encryption.
    SECRET_KEY = os.environ.get("SECRET_KEY") 

    # Database url.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(base_dir, "db.sqlite")

    # OAuth
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    REFRESH_TOKEN_IN_BODY = as_bool(os.environ.get("REFRESH_TOKEN_IN_BODY"))
    REFRESH_TOKEN_IN_COOKIE = as_bool(os.environ.get("REFRESH_TOKEN_IN_COOKIE", "yes"))

    # cross origin resource sharing 
    USE_CORS = as_bool(os.environ.get("USE_CORS"))
