from server import app
from fastapi.testclient import TestClient
import pytest
import datetime


client = TestClient(app)

PERSONAL_API_TOKEN = "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"
SNEAK_PEEK = 120

USERNAME_LIST = [
    "allegro",
    "jakubjnowicki",
    "jph00",
    "CodingTrain",
    "codingforentrepreneurs",
    "techwithtim",
    "SteinOveHelset",
    "sentdex",
    "karoly-zsolnai-feher",
]


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "API About": "github-listing-api is an API written in python using FastAPI framework. API allows (based on github user's repositories) to: list names of repositories, return languages used with their size in bytes used, get all stars count and check current user's requests limits for github api. API has six endpoints receiving only GET requests."
    }


def test_current_limits_without_token():
    response = client.get("/current_limits")
    assert response.status_code == 200
    assert response.json()["current_limits"]["limit"] == 60


def test_current_limits_with_token():
    response = client.get(f"/current_limits/?token={PERSONAL_API_TOKEN}")
    assert response.status_code == 200
    assert response.json()["current_limits"]["limit"] == 5000


@pytest.mark.parametrize("username", USERNAME_LIST)
def test_get_all_repos(username):
    begin_time = datetime.datetime.now()
    url = f"/all_repositories/{username}"
    if PERSONAL_API_TOKEN != "":
        url = url + f"/?token={PERSONAL_API_TOKEN}"
    response = client.get(url)
    print(f"{username}: {datetime.datetime.now() - begin_time}")
    print(f"{response.text}"[:120])
    assert response.status_code == 200


@pytest.mark.parametrize("username", USERNAME_LIST)
def test_get_all_langs(username):
    begin_time = datetime.datetime.now()
    url = f"/all_languages/{username}"
    if PERSONAL_API_TOKEN != "":
        url = url + f"/?token={PERSONAL_API_TOKEN}"
    response = client.get(url)
    print(f"{username}: {datetime.datetime.now() - begin_time}")
    print(f"{response.text}"[:120])
    assert response.status_code == 200


@pytest.mark.parametrize("username", USERNAME_LIST)
def test_get_all_stars(username):
    begin_time = datetime.datetime.now()
    url = f"/all_stars_count/{username}"
    if PERSONAL_API_TOKEN != "":
        url = url + f"/?token={PERSONAL_API_TOKEN}"
    response = client.get(url)

    print(f"{username}, {datetime.datetime.now() - begin_time}")
    print(f"{response.text}"[:120])
    assert response.status_code == 200
