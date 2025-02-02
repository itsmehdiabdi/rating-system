import itertools
import threading
from locust import HttpUser, TaskSet, task, between
import random

POST_COUNT = 3
MAX_RATING = 5

user_id_counter = itertools.count(1)
counter_lock = threading.Lock()


class RateTaskSet(TaskSet):
    def on_start(self):
        with counter_lock:
            self.user_id = next(user_id_counter)
        self.username = f"testuser_{self.user_id}"
        self.username = f"testuser_{self.user_id}"
        self.password = "password"
        self.login()

    def get_csrf_token(self):
        if self.client.cookies.get("csrftoken"):
            return self.client.cookies.get("csrftoken")
        response = self.client.get("/accounts/login/")
        csrf_token = response.cookies.get("csrftoken")
        if not csrf_token:
            print("CSRF token not found during login")
        return csrf_token

    def login(self):
        csrf_token = self.get_csrf_token()
        login_data = {
            "username": self.username,
            "password": self.password,
            "csrfmiddlewaretoken": csrf_token,
        }
        headers = {"Referer": self.client.base_url + "/accounts/login/"}
        response = self.client.post(
            "/accounts/login/", data=login_data, headers=headers)
        if response.status_code != 200:
            print(f"Login failed for {self.username}: {response.text}")

    @task
    def submit_rate(self):
        csrf_token = self.get_csrf_token()
        headers = {
            "X-CSRFToken": csrf_token,
            "Referer": self.client.base_url + "/api/posts/1/rate/"
        }
        post_id = random.randint(1, POST_COUNT)
        rating = random.randint(0, MAX_RATING)
        self.client.post(
            f"/api/posts/{post_id}/rate/", json={"rating": rating}, headers=headers)


class WebsiteUser(HttpUser):
    tasks = [RateTaskSet]
    wait_time = between(0, 0.05)
