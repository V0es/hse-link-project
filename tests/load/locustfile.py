from datetime import datetime, timedelta

from locust import HttpUser, between, task

from app.links.utils import generate_slug
from tests.conftest import basic_auth_headers


class LinkShortenerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        username = "load_user"
        password = "123"
        self.client.post(
            "/auth/register", headers=basic_auth_headers(username, password)
        )
        login_resp = self.client.post(
            "/auth/login", headers=basic_auth_headers(username, password)
        )
        self.token = login_resp.cookies.get("access_token") or login_resp.json().get(
            "access_token"
        )
        self.headers = {"Cookie": f"access_token={self.token}"}

    @task(5)
    def create_link(self):
        payload = {
            "long_url": f"https://example.com/{generate_slug()}",
            "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
        }
        self.client.post("/links/shorten", json=payload, headers=self.headers)

    @task(3)
    def redirect_link(self):
        slug = generate_slug()
        self.client.get(f"/{slug}", headers=self.headers, allow_redirects=False)

    @task(1)
    def relogin(self):
        username = "load_user"
        password = "123"
        self.client.post(
            "/auth/login", json={"username": username, "password": password}
        )
