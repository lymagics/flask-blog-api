import pytest
from time import sleep

from api.models import db, User
from .base_test_case import BaseTestCase


class TestUserModel(BaseTestCase):
    def test_password_is_inaccessible(self):
        u = User(username="alice", password="cat")
        with pytest.raises(AttributeError):
            u.password

    def test_verify_password(self):
        u = User(username="alice", password="cat")
        assert u.verify_password("cat")
        assert u.verify_password("dog") == False

    def test_hash_salts_are_random(self):
        u1 = User(username="alice", password="cat")
        u2 = User(username="charlie", password="cat")
        assert u1.password_hash != u2.password_hash

    def test_ping(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 200

        ping = resp.json["last_seen"]
        sleep(1)
        resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 200
        assert ping != resp.json["last_seen"]

    def test_tokens(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None

        t = u.generate_access_token()
        db.session.commit()
        assert t.access_token is not None 
        assert t.refresh_token is not None 

        u1 = User.verify_access_token(t.access_token)
        assert u1 is not None
        assert u1.username == u.username

        t1 = User.verify_refresh_token(t.refresh_token, t.access_token)
        assert t1 is not None 
        assert t1.refresh_token == t.refresh_token
        assert t1.user_id == u.user_id

    def test_follow(self):
        u1 = User.query.filter_by(username="bob").first()
        assert u1 is not None 

        u2 = User(username="alice", email="alice@example.com", password="dog")
        db.session.add(u2)
        db.session.commit()

        u1.follow(u2)
        db.session.commit()

        assert u1.is_following(u2)
        assert u2.is_followed_by(u1)
        assert u2.is_following(u1) == False

    def test_unfollow(self):
        u1 = User.query.filter_by(username="bob").first()
        assert u1 is not None 

        u2 = User(username="alice", email="alice@example.com", password="dog")
        db.session.add(u2)
        db.session.commit()

        u1.follow(u2)
        db.session.commit()

        u1.unfollow(u2)
        db.session.commit()

        assert u1.is_following(u2) == False 
        assert u2.is_followed_by(u1) == False
