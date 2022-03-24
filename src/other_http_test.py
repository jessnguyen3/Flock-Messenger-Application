from time import sleep
import re
from subprocess import Popen, PIPE
import signal
import requests
import pytest


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
    """ Supply first user - returns their token and u_id."""
    user_registration = {
        "email": "valid@gmail.com",
        "password": "password",
        "name_first": "firstname",
        "name_last": "lastname",
    }
    user_req = requests.post(f"{url}/auth/register", json=user_registration)
    return user_req.json()


@pytest.fixture
def supply_user2(url):
    """ Supply second user - returns their token and u_id."""
    user_registration = {
        "email": "somevalid@gmail.com",
        "password": "password",
        "name_first": "first",
        "name_last": "last",
    }
    user_req = requests.post(f"{url}/auth/register", json=user_registration)
    return user_req.json()


def test_all_users_http(url, supply_user1, supply_user2):
    """
    Test that route /users/all can be called and user is returned
    a list of all the users in the Flockr.
    """
    users_req = requests.get(
        f"{url}/users/all", params={"token": supply_user1["token"]}
    )
    assert users_req.status_code == 200
    users_list = users_req.json()["users"]
    assert len(users_list) == 2


def test_search_empty_http(url, supply_user1):
    """
    Search for messages without any being sent yet.
    """
    message_req = requests.get(
        f"{url}/search", params={"token": supply_user1["token"], "query_str": "message"}
    )
    assert message_req.status_code == 200
    messages_list = message_req.json()["messages"]
    assert messages_list == []


def test_search_messages_found_http(url, supply_user1):
    """
    Search for messages and ensure a list of messages is returned to the user.
    """
    data = {"token": supply_user1["token"], "name": "channel", "is_public": True}
    channel_req = requests.post(f"{url}/channels/create", json=data)
    channel_id = channel_req.json()["channel_id"]

    # Sending messages below
    message1 = {
        "token": supply_user1["token"],
        "channel_id": channel_id,
        "message": "This is a message",
    }
    requests.post(f"{url}/message/send", json=message1)
    message2 = {
        "token": supply_user1["token"],
        "channel_id": channel_id,
        "message": "Last message",
    }
    requests.post(f"{url}/message/send", json=message2)
    message3 = {
        "token": supply_user1["token"],
        "channel_id": channel_id,
        "message": "Okay maybe not.",
    }
    requests.post(f"{url}/message/send", json=message3)

    # Testing the search function
    message_req = requests.get(
        f"{url}/search", params={"token": supply_user1["token"], "query_str": "message"}
    )
    assert message_req.status_code == 200
    messages_list = message_req.json()["messages"]
    assert len(messages_list) == 2
