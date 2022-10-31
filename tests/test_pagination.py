from api.models import db, User, Post
from .base_test_case import BaseTestCase


class TestPagination(BaseTestCase):
    def test_retrieve_all_users(self):
        resp = self.client.get("/users?limit=2")
        assert resp.status_code == 200
        assert "users" in resp.json 
        assert "pagination" in resp.json 
        assert resp.json["pagination"]["limit"] == 2
        assert resp.json["pagination"]["offset"] == 0
        assert len(resp.json["users"]) == 1

    def test_retrieve_all_posts(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None 

        p1 = Post(author=u, title="Post 1", content="Content of post 1")
        p2 = Post(author=u, title="Post 2", content="Content of post 2")
        db.session.add_all([p1, p2])
        db.session.commit()

        resp = self.client.get("/posts?limit=2")
        assert resp.status_code == 200 
        assert "posts" in resp.json 
        assert "pagination" in resp.json 
        assert resp.json["pagination"]["limit"] == 2
        assert resp.json["pagination"]["offset"] == 0
        assert len(resp.json["posts"]) == 2

    def test_retrieve_all_user_posts(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None 

        p1 = Post(author=u, title="Post 1", content="Content of post 1")
        p2 = Post(author=u, title="Post 2", content="Content of post 2")
        db.session.add_all([p1, p2])
        db.session.commit()

        resp = self.client.get("/users/1/posts?limit=2")
        assert resp.status_code == 200 
        assert "posts" in resp.json 
        assert "pagination" in resp.json 
        assert resp.json["pagination"]["limit"] == 2
        assert resp.json["pagination"]["offset"] == 0
        assert len(resp.json["posts"]) == 2

        u2 = User(username="alice", email="alice@example.com", password="dog")
        db.session.add(u2)
        db.session.commit()

        resp = self.client.get("/users/2/posts?limit=2")
        assert resp.status_code == 200 
        assert "posts" in resp.json 
        assert "pagination" in resp.json 
        assert resp.json["pagination"]["limit"] == 2
        assert resp.json["pagination"]["offset"] == 0
        assert len(resp.json["posts"]) == 0

    def test_retrieve_my_followed(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None 

        u2 = User(username="alice", email="alice@example.com", password="dog")
        db.session.add(u2)
        db.session.commit()

        u.follow(u2)
        db.session.commit()

        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        resp = self.client.get("/me/following?limit=2", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 200
        assert "users" in resp.json 
        assert "pagination" in resp.json 
        assert resp.json["pagination"]["limit"] == 2
        assert resp.json["pagination"]["offset"] == 0
        assert len(resp.json["users"]) == 1

    def test_retrieve_my_followers(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None 

        u2 = User(username="alice", email="alice@example.com", password="dog")
        db.session.add(u2)
        db.session.commit()

        u2.follow(u)
        db.session.commit()

        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        resp = self.client.get("/me/followers?limit=2", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 200
        assert "users" in resp.json 
        assert "pagination" in resp.json 
        assert resp.json["pagination"]["limit"] == 2
        assert resp.json["pagination"]["offset"] == 0
        assert len(resp.json["users"]) == 1

    def test_retrieve_user_followed(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None 

        u2 = User(username="alice", email="alice@example.com", password="dog")
        db.session.add(u2)
        db.session.commit()

        u.follow(u2)
        db.session.commit() 

        resp = self.client.get("/users/1/following?limit=2")
        assert resp.status_code == 200
        assert "users" in resp.json 
        assert "pagination" in resp.json 
        assert resp.json["pagination"]["limit"] == 2
        assert resp.json["pagination"]["offset"] == 0
        assert len(resp.json["users"]) == 1

    def test_retrieve_user_followers(self):
        u = User.query.filter_by(username="bob").first()
        assert u is not None 

        u2 = User(username="alice", email="alice@example.com", password="dog")
        db.session.add(u2)
        db.session.commit()

        u2.follow(u)
        db.session.commit()

        resp = self.client.get("/users/1/followers?limit=2")
        assert resp.status_code == 200
        assert "users" in resp.json 
        assert "pagination" in resp.json 
        assert resp.json["pagination"]["limit"] == 2
        assert resp.json["pagination"]["offset"] == 0
        assert len(resp.json["users"]) == 1
