import requests
import signal
import pytest
import re
from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime

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
            "email": "person1@mail.com",
            "password": "password",
            "name_first": "firstname",
            "name_last": "lastname",
        },
    ).json()


@pytest.fixture
def supply_channel(url, supply_user):
    return requests.post(
        f"{url}/channels/create",
        json={
            "token": supply_user["token"],
            "name": "channel",
            "is_public": True,
        },
    ).json()


@pytest.fixture
def supply_message(url, supply_user, supply_channel):
    return requests.post(
        f"{url}/message/send",
        json={
            "token": supply_user["token"],
            "channel_id": supply_channel["channel_id"],
            "message": "this is a message",
        },
    ).json()


def test_message_send_http(url, supply_user, supply_channel):
    # message/send = POST
    sent_message = requests.post(
        f"{url}/message/send",
        json={
            "token": supply_user["token"],
            "channel_id": supply_channel["channel_id"],
            "message": "this is a message",
        },
    )
    # 200 = success
    assert sent_message.status_code == 200

    channel_message = requests.get(
        f"{url}/channel/messages",
        params={
            "token": supply_user["token"],
            "channel_id": supply_channel["channel_id"],
            "start": 0,
        },
    ).json()

    assert channel_message["messages"][0]["message"] == "this is a message"


def test_message_edit_http(url, supply_user, supply_channel, supply_message):
    # message/edit = PUT
    edit_message = requests.put(
        f"{url}/message/edit",
        json={
            "token": supply_user["token"],
            "message_id": supply_message["message_id"],
            "message": "Better message",
        },
    )

    channel_messages = requests.get(
        f"{url}/channel/messages",
        params={
            "token": supply_user["token"],
            "channel_id": supply_channel["channel_id"],
            "start": 0,
        },
    ).json()

    assert edit_message.status_code == 200
    assert channel_messages["messages"][0]["message"] == "Better message"


def test_message_remove_http(url, supply_user, supply_channel, supply_message):
    # mesage/remove = DELETE
    assert (
        requests.delete(
            f"{url}/message/remove",
            json={
                "token": supply_user["token"],
                "message_id": supply_message["message_id"],
            },
        ).status_code
        == 200
    )

    assert (
        len(
            requests.get(
                f"{url}/channel/messages",
                params={
                    "token": supply_user["token"],
                    "channel_id": supply_channel["channel_id"],
                    "start": 0,
                },
            ).json()["messages"]
        )
        == 0
    )


def test_message_sendlater_http(url, supply_user, supply_channel, supply_message):
    data = {
        "token": supply_user["token"],
        "channel_id": supply_channel["channel_id"],
        "message": "This is a message.",
        "time_sent": int(datetime.utcnow().strftime("%s")) + 10,
    }
    assert requests.post(f"{url}/message/sendlater", json=data).status_code == 200


def test_message_react_http(url, supply_user, supply_message):
    data = {
        "token": supply_user["token"],
        "message_id": supply_message["message_id"],
        "react_id": 1,
    }
    assert requests.post(f"{url}/message/react", json=data).status_code == 200


def test_message_unreact_http(url, supply_user, supply_message):
    data = {
        "token": supply_user["token"],
        "message_id": supply_message["message_id"],
        "react_id": 1,
    }
    requests.post(f"{url}/message/react", json=data).status_code
    assert requests.post(f"{url}/message/unreact", json=data).status_code == 200


def test_message_pin_http(url, supply_user, supply_message):
    data = {
        "token": supply_user["token"],
        "message_id": supply_message["message_id"],
    }
    assert requests.post(f"{url}/message/pin", json=data).status_code == 200


def test_message_unpin_http(url, supply_user, supply_message):
    data = {
        "token": supply_user["token"],
        "message_id": supply_message["message_id"],
    }
    requests.post(f"{url}/message/pin", json=data)
    assert requests.post(f"{url}/message/unpin", json=data).status_code == 200
