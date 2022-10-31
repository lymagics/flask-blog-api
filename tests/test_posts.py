from .base_test_case import BaseTestCase


class TestPosts(BaseTestCase):
    def test_create_post(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        data = {
            "title": "RestAPI tutorial",
            "content": "Create restful api with Flask"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201
        assert resp.json["title"] == "RestAPI tutorial"
        assert resp.json["content"] == "Create restful api with Flask"
        assert "created_at" in resp.json 
        assert "post_id" in resp.json 
        assert "author" in resp.json 
        assert resp.json["author"]["username"] == "bob"

    def test_retrieve_post_by_id(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        data = {
            "title": "RestAPI tutorial",
            "content": "Create restful api with Flask"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201

        resp = self.client.get("/posts/1")
        assert resp.status_code == 200

        resp = self.client.get("/posts/2")
        assert resp.status_code == 404

    def test_update_post(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        data = {
            "title": "RestAPI tutorial",
            "content": "Create restful api with Flask"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201

        update_data = {
            "title": "Another title",
            "content": "Another content"
        }
        resp = self.client.put("/posts/1", headers={"Authorization": f"Bearer {access_token}"}, json=update_data)
        assert resp.status_code == 200
        assert resp.json["title"] != data["title"]
        assert resp.json["content"] != data["content"]

    def test_delete_post(self):
        resp = self.client.post("/tokens", auth=("bob", "cat"))
        assert resp.status_code == 201
        access_token = resp.json["access_token"]

        data = {
            "title": "RestAPI tutorial",
            "content": "Create restful api with Flask"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201

        resp = self.client.delete("/posts/1", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 204

        resp = self.client.delete("/posts/1", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 404
