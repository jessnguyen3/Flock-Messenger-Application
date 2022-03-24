import requests
import signal
import pytest
import re
from subprocess import Popen, PIPE
from time import sleep


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


@pytest.fixture
def supply_user(url):
    return requests.post(
        f"{url}/auth/register",
        json={
            "email": "frankyan@mail.com",
            "password": "123abc!@#",
            "name_first": "Frank",
            "name_last": "Yan",
        },
    ).json()


def test_user_profile_http(url, supply_user):
    # testing user/profile
    profile_req = requests.get(
        f"{url}/user/profile",
        params={"token": supply_user["token"], "u_id": supply_user["u_id"]},
    )

    assert profile_req.status_code == 200
    assert profile_req.json() == {
        "u_id": supply_user["u_id"],
        "email": "frankyan@mail.com",
        "name_first": "Frank",
        "name_last": "Yan",
        "handle_str": "frank",
    }


def test_user_profile_setname_http(url, supply_user):
    setname = requests.put(
        f"{url}/user/profile/setname",
        json={
            "token": supply_user["token"],
            "name_first": "Hank",
            "name_last": "Yang",
        },
    )

    user = requests.get(
        f"{url}/user/profile",
        params={"token": supply_user["token"], "u_id": supply_user["u_id"]},
    ).json()

    assert setname.status_code == 200
    assert user["name_first"] == "Hank"
    assert user["name_last"] == "Yang"


def test_user_profile_setemail_http(url, supply_user):
    assert (
        requests.put(
            f"{url}/user/profile/setemail",
            json={"token": supply_user["token"], "email": "hankyang@mail.com"},
        ).status_code
        == 200
    )

    user = (
        requests.get(
            f"{url}/user/profile",
            params={"token": supply_user["token"], "u_id": supply_user["u_id"]},
        )
    ).json()

    assert user["email"] == "hankyang@mail.com"


def test_user_profile_sethandle_http(url, supply_user):
    # testing user/profile/sethandle
    assert (
        requests.put(
            f"{url}/user/profile/sethandle",
            json={"token": supply_user["token"], "handle_str": "hank"},
        ).status_code
        == 200
    )

    assert (
        requests.get(
            f"{url}/user/profile",
            params={"token": supply_user["token"], "u_id": supply_user["u_id"]},
        ).json()["handle_str"]
        == "hank"
    )
