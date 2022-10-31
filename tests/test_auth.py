from datetime import datetime, timedelta
from unittest import mock
from .base_test_case import BaseTestCase


class TestAuth(BaseTestCase):
    def test_no_auth(self):
        resp = self.client.get("/me")
        assert resp.status_code == 401

    def test_bad_credentials(self):
        resp = self.client.get("/me", auth=("alice", "dog"))
        assert resp.status_code == 401

    def test_get_token(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201

        access_token = resp.json["access_token"]
        refresh_token = resp.json["refresh_token"]

        resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 200
        assert resp.json["username"] == "bob"

        resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token}x"})
        assert resp.status_code == 401

        resp = self.client.get("/me", headers={"Authorization": f"Bearer {refresh_token}"})
        assert resp.status_code == 401

    def test_refresh_token_in_body_only(self):
        self.app.config["REFRESH_TOKEN_IN_BODY"] = True 
        self.app.config["REFRESH_TOKEN_IN_COOKIE"] = False 

        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        assert resp.json["refresh_token"] is not None
        assert "Set-Cookie" not in resp.headers

    def test_refresh_token_in_cookie_only(self):
        self.app.config["REFRESH_TOKEN_IN_BODY"] = False 
        self.app.config["REFRESH_TOKEN_IN_COOKIE"] = True 

        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        assert resp.json["refresh_token"] is None 
        assert resp.headers["Set-Cookie"].startswith("refresh_token=")

    def test_token_expired(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        with mock.patch("api.models.datetime") as dt:
            dt.utcnow.return_value = datetime.utcnow() + timedelta(days=1)
            resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
            assert resp.status_code == 401

    def test_refresh_token(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token1 = resp.json["access_token"]
        refresh_token1 = resp.json["refresh_token"]

        resp = self.client.put("/tokens", json={"access_token": access_token1}, headers={"Cookie": f"refresh_token={refresh_token1}"})
        assert resp.status_code == 201 
        assert resp.json["access_token"] != access_token1
        assert resp.json["refresh_token"] != refresh_token1
        access_token2 = resp.json["access_token"]

        resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token2}"})
        assert resp.status_code == 200
        assert resp.json["username"] == "bob"

        resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token1}"})
        assert resp.status_code == 401

    def test_revoke_token(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201

        access_token = resp.json["access_token"]
        resp = self.client.delete("/tokens", json={"access_token": access_token})
        assert resp.status_code == 204

        resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 401



