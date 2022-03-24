import pytest
from auth import auth_register
from channel import channel_details, channel_join
from channels import *
from error import InputError, AccessError
from other import clear


@pytest.fixture
def supply_user():
    clear()
    return auth_register("validemail@gmail.com", "123abc!@#", "First", "Last")


@pytest.fixture
def supply_user2():
    return auth_register("otheremail@gmail.com", "123abc!@#", "First", "Last")


@pytest.fixture
def supply_channels(supply_user, supply_user2):
    channels_create(supply_user["token"], "A", True)
    result = channels_create(supply_user2["token"], "B", True)
    channel_join(supply_user["token"], result["channel_id"])
    channels_create(supply_user2["token"], "C", True)


def test_channels_list(supply_user, supply_channels):
    channels = channels_list(supply_user["token"])["channels"]
    assert len(channels) == 2
    assert "A" in [channel["name"] for channel in channels]
    assert "B" in [channel["name"] for channel in channels]


def test_channels_listall(supply_user, supply_channels):
    channels = channels_listall(supply_user["token"])["channels"]
    assert len(channels) == 3
    channel_names = [channel["name"] for channel in channels]
    assert all(x in channel_names for x in ["A", "B", "C"])


def test_channels_create(supply_user, supply_user2):
    result = channels_create(supply_user["token"], "Test", False)
    assert len(data["channels"]) == 1
    assert channel_details(supply_user["token"], result["channel_id"]) == {
        "name": "Test",
        "owner_members": [
            {"u_id": supply_user["u_id"], "name_first": "First", "name_last": "Last"}
        ],
        "all_members": [],
    }


def test_channels_create_id_unique(supply_user):
    channel_id_list = []
    for _ in range(100):
        result = channels_create(supply_user["token"], "Test", True)
        channel_id_list.append(result["channel_id"])
    assert len(set(channel_id_list)) == 100


def test_channels_list_exception(supply_user):
    print(data["sessions"])
    with pytest.raises(AccessError):
        channels_list(0)


def test_channels_listall_exception(supply_user):
    print(data["sessions"])
    with pytest.raises(AccessError):
        channels_listall(0)


def test_channels_create_exception(supply_user):
    with pytest.raises(AccessError):
        channels_create(0, "Test", True)
    with pytest.raises(InputError):
        channels_create(supply_user["token"], "namelongerthan20chars", False)
