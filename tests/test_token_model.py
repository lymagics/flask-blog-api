from datetime import datetime, timedelta
from time import sleep

from api.models import db, User, Token
from .base_test_case import BaseTestCase


class TestTokenModel(BaseTestCase):
    def test_generate_token(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None 

        t = Token(user=u)
        t.generate()
        assert t.access_token is not None 
        assert t.refresh_token is not None 
        assert t.access_expiration > datetime.utcnow()
        assert t.refresh_expiration > datetime.utcnow()

    def test_token_expire(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None 

        t = Token(user=u)
        t.generate()
        t.expire()
        sleep(1)

        assert t.access_expiration < datetime.utcnow()
        assert t.refresh_expiration < datetime.utcnow()

    def test_clean_token_table(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None 

        t = Token(user=u)
        t.generate()
        t.refresh_expiration = datetime.utcnow() - timedelta(days=2)
        db.session.add(t)
        db.session.commit()

        Token.clean()
        db.session.commit()

        assert Token.query.all() == []
