from .base_test_case import BaseTestCase


class TestUsers(BaseTestCase):
    def test_create_user(self):
        data = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "dog"
        }
        resp = self.client.post("/users", json=data)
        assert resp.status_code == 201
        assert resp.json["username"] == "alice"
        assert "user_id" in resp.json
        assert "last_seen" in resp.json
        assert "member_since" in resp.json
        assert "password" not in resp.json 
        assert "email" not in resp.json

        wrong_data = {
            "username": "alice",
            "email": "helloworld"
        }
        resp = self.client.post("/users", json=wrong_data)
        assert resp.status_code == 400

    def test_retrieve_user_by_id(self):
        resp = self.client.get("/users/1")
        assert resp.status_code == 200
        assert resp.json["username"] == "bob"
        assert "user_id" in resp.json
        assert "last_seen" in resp.json
        assert "member_since" in resp.json
        assert "password" not in resp.json 
        assert "email" not in resp.json

        resp = self.client.get("/users/555")
        assert resp.status_code == 404

    def test_retrieve_user_by_username(self):
        resp = self.client.get("/users/bob")
        assert resp.status_code == 200
        assert resp.json["username"] == "bob"
        assert "user_id" in resp.json
        assert "last_seen" in resp.json
        assert "member_since" in resp.json
        assert "password" not in resp.json 
        assert "email" not in resp.json

        resp = self.client.get("/users/alice")
        assert resp.status_code == 404

    def test_retrieve_authenticated_user(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 200
        assert resp.json["username"] == "bob"
        assert "user_id" in resp.json
        assert "last_seen" in resp.json
        assert "member_since" in resp.json
        assert "password" not in resp.json 
        assert "email" not in resp.json

        resp = self.client.post("/tokens", auth=("bob", "dog"))
        assert resp.status_code == 401

    def test_update_authenticated_user(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        data = {
            "username": "alice",
            "email": "alice@example.com",
            "old_password": "cat",
            "password": "dog"
        }

        resp = self.client.put("/me", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 200

        wrong_data = {
            "email": "helloworld",
            "old_password": "cat",
            "password": "dog"
        }
        resp = self.client.put("/me", headers={"Authorization": f"Bearer {access_token}"}, json=wrong_data)
        assert resp.status_code == 400

