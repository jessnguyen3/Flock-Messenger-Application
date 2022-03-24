import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests

from json import dumps

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    url_re = re.compile(r" \* Running on ([^ ]*)")
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")


@pytest.fixture()
def supply_user(url):
    return requests.post(
        f"{url}/auth/register",
        json={
            "email": "person1@mail.com",
            "password": "password",
            "name_first": "firstname",
            "name_last": "lastname",
        },
    ).json()


def test_auth_register_http(url):
    register_req = requests.post(
        f"{url}/auth/register",
        json={
            "email": "person1@mail.com",
            "password": "password",
            "name_first": "firstname",
            "name_last": "lastname",
        },
    )

    assert register_req.status_code == 200
    assert register_req.json()["u_id"] is not None
    assert register_req.json()["token"] is not None


def test_auth_logout(url, supply_user):
    logout_req = requests.post(
        f"{url}/auth/logout", json={"token": supply_user["token"]}
    )

    assert logout_req.status_code == 200
    assert logout_req.json()["is_success"]


def test_auth_login(url, supply_user):
    requests.post(
        f"{url}/auth/logout",
        json={"token": supply_user["token"]},
    )

    login_req = requests.post(
        f"{url}/auth/login", json={"email": "person1@mail.com", "password": "password"}
    )

    assert login_req.status_code == 200
    assert login_req.json()["u_id"] is not None
    assert login_req.json()["token"] is not None
