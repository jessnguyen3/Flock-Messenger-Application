import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from channel import *
from auth import auth_register
from channels import channels_create
from other import clear
from message import message_send


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
def supply_user1(url):
    return requests.post(
        f"{url}/auth/register",
        json={
            "email": "user1@gmail.com",
            "password": "123abc!@#",
            "name_first": "Frank",
            "name_last": "Yan",
        },
    ).json()


@pytest.fixture
def supply_user2(url):
    return requests.post(
        f"{url}/auth/register",
        json={
            "email": "user2@gmail.com",
            "password": "123abc!@#",
            "name_first": "Hank",
            "name_last": "Yang",
        },
    ).json()


@pytest.fixture
def supply_channel(url, supply_user1, supply_user2):
    return requests.post(
        f"{url}/channels/create",
        json={
            "token": supply_user1["token"],
            "name": "Test Channel",
            "is_public": True,
        },
    ).json()


def test_channel_details_http(url, supply_user1, supply_channel):
    channel_details = requests.get(
        f"{url}/channel/details",
        params={
            "token": supply_user1["token"],
            "channel_id": supply_channel["channel_id"],
        },
    )

    assert channel_details.status_code == 200
    assert channel_details.json() == {
        "name": "Test Channel",
        "owner_members": [
            {
                "u_id": supply_user1["u_id"],
                "name_first": "Frank",
                "name_last": "Yan",
            }
        ],
        "all_members": [],
    }


def test_channel_invite_http(url, supply_user1, supply_user2, supply_channel):
    assert (
        requests.post(
            f"{url}/channel/invite",
            json={
                "token": supply_user1["token"],
                "channel_id": supply_channel["channel_id"],
                "u_id": supply_user2["u_id"],
            },
        ).status_code
        == 200
    )

    all_members = requests.get(
        f"{url}/channel/details",
        params={
            "token": supply_user1["token"],
            "channel_id": supply_channel["channel_id"],
        },
    ).json()["all_members"]

    assert supply_user2["u_id"] in [member["u_id"] for member in all_members]


def test_channel_messages_http(url, supply_user1, supply_channel):
    messages = requests.get(
        f"{url}/channel/messages",
        params={
            "token": supply_user1["token"],
            "channel_id": supply_channel["channel_id"],
            "start": 0,
        },
    )

    assert messages.status_code == 200
    assert messages.json() == {
        "messages": [],
        "start": 0,
        "end": -1,
    }


def test_channel_leave_http(url, supply_user1, supply_user2, supply_channel):
    requests.post(
        f"{url}/channel/invite",
        json={
            "token": supply_user1["token"],
            "channel_id": supply_channel["channel_id"],
            "u_id": supply_user2["u_id"],
        },
    )

    assert (
        requests.post(
            f"{url}/channel/leave",
            json={
                "token": supply_user2["token"],
                "channel_id": supply_channel["channel_id"],
            },
        ).status_code
        == 200
    )

    all_members = requests.get(
        f"{url}/channel/details",
        params={
            "token": supply_user1["token"],
            "channel_id": supply_channel["channel_id"],
        },
    ).json()["all_members"]

    assert supply_user2["u_id"] not in [member["u_id"] for member in all_members]


def test_channel_join_http(url, supply_user1, supply_user2, supply_channel):
    assert (
        requests.post(
            f"{url}/channel/join",
            json={
                "token": supply_user2["token"],
                "channel_id": supply_channel["channel_id"],
            },
        ).status_code
        == 200
    )

    all_members = requests.get(
        f"{url}/channel/details",
        params={
            "token": supply_user1["token"],
            "channel_id": supply_channel["channel_id"],
        },
    ).json()["all_members"]

    assert supply_user2["u_id"] in [member["u_id"] for member in all_members]


def test_channel_addowner_http(url, supply_user1, supply_user2, supply_channel):
    requests.post(
        f"{url}/channel/join",
        json={
            "token": supply_user2["token"],
            "channel_id": supply_channel["channel_id"],
        },
    )

    assert (
        requests.post(
            f"{url}/channel/addowner",
            json={
                "token": supply_user1["token"],
                "channel_id": supply_channel["channel_id"],
                "u_id": supply_user2["u_id"],
            },
        ).status_code
        == 200
    )

    owner_members = requests.get(
        f"{url}/channel/details",
        params={
            "token": supply_user1["token"],
            "channel_id": supply_channel["channel_id"],
        },
    ).json()["owner_members"]

    assert supply_user2["u_id"] in [member["u_id"] for member in owner_members]


def test_channel_removeowner_http(url, supply_user1, supply_user2, supply_channel):
    requests.post(
        f"{url}/channel/join",
        json={
            "token": supply_user2["token"],
            "channel_id": supply_channel["channel_id"],
        },
    )

    requests.post(
        f"{url}/channel/addowner",
        json={
            "token": supply_user1["token"],
            "channel_id": supply_channel["channel_id"],
            "u_id": supply_user2["u_id"],
        },
    )

    assert (
        requests.post(
            f"{url}/channel/removeowner",
            json={
                "token": supply_user1["token"],
                "channel_id": supply_channel["channel_id"],
                "u_id": supply_user2["u_id"],
            },
        ).status_code
        == 200
    )

    owner_members = requests.get(
        f"{url}/channel/details",
        params={
            "token": supply_user1["token"],
            "channel_id": supply_channel["channel_id"],
        },
    ).json()["owner_members"]

    assert supply_user2["u_id"] not in [member["u_id"] for member in owner_members]
