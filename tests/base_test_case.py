import unittest 

from api import create_app, db
from api.models import User
from config import Config


class TestConfig(Config):
    TESTING = True 
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    REFRESH_TOKEN_IN_BODY = True


class BaseTestCase(unittest.TestCase):
    config = TestConfig

    def setUp(self):
        self.app = create_app(self.config)
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        db.create_all()
        user = User(username="bob", email="bob@example.com", password="cat")
        db.session.add(user)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.drop_all()
        self.app_ctx.pop()
