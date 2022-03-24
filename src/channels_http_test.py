import re
from subprocess import Popen, PIPE
import signal
from time import sleep
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
    user_registration = {
        "email": "somevalid@gmail.com",
        "password": "password",
        "name_first": "first",
        "name_last": "last",
    }
    user_req = requests.post(f"{url}/auth/register", json=user_registration)
    return user_req.json()


@pytest.fixture
def supply_channel_id1(url, supply_user1):
    """ Create first channel and return its channel id."""
    data = {"token": supply_user1["token"], "name": "first_channel", "is_public": True}
    channel_req = requests.post(f"{url}/channels/create", json=data)
    return channel_req.json()["channel_id"]


@pytest.fixture
def supply_channel_id2(url, supply_user2):
    """ Create second channel and return its channel id."""
    data = {"token": supply_user2["token"], "name": "second_channel", "is_public": True}
    channel_req = requests.post(f"{url}/channels/create", json=data)
    return channel_req.json()["channel_id"]


# Test channels_list
def test_list_none_http(url, supply_user1):
    """
    With no channels created, test that an empty list is returned to user.
    """
    list_req = requests.get(
        f"{url}/channels/list", params={"token": supply_user1["token"]}
    )
    assert list_req.status_code == 200
    user_channels = list_req.json()["channels"]
    assert user_channels == []


def test_list_channels_returned_http(
    url, supply_user1, supply_user2, supply_channel_id1, supply_channel_id2
):
    """
    With channels created, test that a list of channels the user is in is returned.
    """
    data = {
        "token": supply_user2["token"],
        "channel_id": supply_channel_id1,
    }
    requests.post(f"{url}/channel/join", json=data)

    list_req = requests.get(
        f"{url}/channels/list", params={"token": supply_user1["token"]}
    )
    assert list_req.status_code == 200
    user_channels = list_req.json()["channels"]
    assert len(user_channels) == 1

    list_req = requests.get(
        f"{url}/channels/list", params={"token": supply_user2["token"]}
    )
    assert list_req.status_code == 200
    user_channels = list_req.json()["channels"]
    assert len(user_channels) == 2


# Test channels_listall
def test_listall_none_http(url, supply_user1):
    """
    With no channels created, test that an empty list is returned to user.
    """
    listall_req = requests.get(
        f"{url}/channels/listall", params={"token": supply_user1["token"]}
    )
    assert str(listall_req.status_code)[0] == "2"
    all_channels = listall_req.json()["channels"]
    assert all_channels == []


def test_listall_channels_returned_http(
    url, supply_user1, supply_channel_id1, supply_channel_id2
):
    """
    With channels created, test that a list of all channels is returned to the user.
    """
    listall_req = requests.get(
        f"{url}/channels/listall", params={"token": supply_user1["token"]}
    )
    assert listall_req.status_code == 200
    all_channels = listall_req.json()["channels"]

    assert len(all_channels) == 2


# Test channels_create
def test_channels_create_http(url, supply_user1):
    """
    Test that a channel can be created and that the data sent back to the user
    is the channel_id of the channel they just created.
    """
    data = {"token": supply_user1["token"], "name": "channel", "is_public": True}
    creation_req = requests.post(f"{url}/channels/create", json=data)
    assert str(creation_req.status_code)[0] == "2"
    channel_id = str(creation_req.json()["channel_id"])
    assert channel_id.isdigit()
