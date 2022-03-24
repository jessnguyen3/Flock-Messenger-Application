import pytest
from auth import auth_register
from channel import channel_join, channel_messages
from channels import channels_create
from error import InputError, AccessError
from message import *
from other import clear
import time


@pytest.fixture
def supply_user():
    clear()
    return auth_register("validemail@gmail.com", "123abc!@#", "First", "Last")


@pytest.fixture
def supply_channels(supply_user):
    channels_create(supply_user["token"], "A", True)
    result = channels_create(supply_user["token"], "B", True)
    channel_join(supply_user["token"], result["channel_id"])
    return result


def test_message_send(supply_user, supply_channels):
    message_send(supply_user["token"], supply_channels["channel_id"], "Test")
    result = channel_messages(supply_user["token"], supply_channels["channel_id"], 0)
    assert len(result["messages"]) == 1
    message = result["messages"][0]
    assert message["u_id"] == supply_user["u_id"]
    assert message["message"] == "Test"


def test_message_send_invalid_channel_id(supply_user, supply_channels):
    with pytest.raises(InputError):
        message_send(supply_user["token"], supply_channels["channel_id"] + 1, "Test")


def test_message_send_id_unique(supply_user, supply_channels):
    for _ in range(50):
        message_send(supply_user["token"], supply_channels["channel_id"], "Test")
    result = channel_messages(supply_user["token"], supply_channels["channel_id"], 0)
    message_id_list = [message["message_id"] for message in result["messages"]]
    assert len(set(message_id_list)) == 50


def test_message_remove(supply_user, supply_channels):
    message_send(supply_user["token"], supply_channels["channel_id"], "Test")
    result = channel_messages(supply_user["token"], supply_channels["channel_id"], 0)
    message_remove(supply_user["token"], result["messages"][0]["message_id"])
    result = channel_messages(supply_user["token"], supply_channels["channel_id"], 0)
    assert result["messages"] == []


def test_message_edit(supply_user, supply_channels):
    message_send(supply_user["token"], supply_channels["channel_id"], "Test")
    result = channel_messages(supply_user["token"], supply_channels["channel_id"], 0)
    message_edit(supply_user["token"], result["messages"][0]["message_id"], "Tset")
    result = channel_messages(supply_user["token"], supply_channels["channel_id"], 0)
    assert result["messages"][0]["message"] == "Tset"


def test_message_send_exception(supply_user, supply_channels):
    with pytest.raises(AccessError):
        message_send(0, supply_channels["channel_id"], "Test")
    with pytest.raises(InputError):
        message_send(supply_user["token"], supply_channels["channel_id"], "Test" * 251)
    result = auth_register("otheremail@gmail.com", "123abc!@#", "First", "Last")
    with pytest.raises(AccessError):
        message_send(0, supply_channels["channel_id"], "Test")
        message_send(result["token"], supply_channels["channel_id"], "Test")


def test_message_remove_exception(supply_user, supply_channels):
    with pytest.raises(InputError):
        message_remove(supply_user["token"], 0)
    new_user = auth_register("otheremail@gmail.com", "123abc!@#", "First", "Last")
    channel_join(new_user["token"], supply_channels["channel_id"])
    message_send(supply_user["token"], supply_channels["channel_id"], "Test")
    result = channel_messages(supply_user["token"], supply_channels["channel_id"], 0)
    with pytest.raises(AccessError):
        message_remove(0, result["messages"][0]["message_id"])
    with pytest.raises(AccessError):
        message_remove(new_user["token"], result["messages"][0]["message_id"])


def test_message_edit_exception(supply_user, supply_channels):
    new_user = auth_register("otheremail@gmail.com", "123abc!@#", "First", "Last")
    channel_join(new_user["token"], supply_channels["channel_id"])
    message_send(supply_user["token"], supply_channels["channel_id"], "Test")
    result = channel_messages(supply_user["token"], supply_channels["channel_id"], 0)
    with pytest.raises(AccessError):
        message_edit(0, result["messages"][0]["message_id"], "Tset")
    with pytest.raises(AccessError):
        message_edit(new_user["token"], result["messages"][0]["message_id"], "Tset")


def test_message_sendlater_invalid_time(supply_user, supply_channels):
    invalid_time = int(time.time()) - 100
    with pytest.raises(InputError):
        message_sendlater(
            supply_user["token"], supply_channels["channel_id"], "message", invalid_time
        )


def test_message_react_invalid_react_id(supply_user, supply_channels):
    msg_id = message_send(
        supply_user["token"], supply_channels["channel_id"], "Some message"
    )["message_id"]
    with pytest.raises(InputError):
        message_react(supply_user["token"], msg_id, 0)


def test_message_react_user_unjoined(supply_user):
    new_user = auth_register("owner@gmail.com", "Password", "Owner", "Name")
    channel_id = channels_create(new_user["token"], "Channel", True)["channel_id"]
    msg_id = message_send(new_user["token"], channel_id, "Some message")["message_id"]
    with pytest.raises(InputError):
        message_react(supply_user["token"], msg_id, 1)


def test_message_react_valid(supply_user, supply_channels):
    msg_id = message_send(
        supply_user["token"], supply_channels["channel_id"], "Some message"
    )["message_id"]
    message_react(supply_user["token"], msg_id, 1)
    with pytest.raises(InputError):
        message_react(supply_user["token"], msg_id, 1)


def test_message_unreact_invalid_react_id(supply_user, supply_channels):
    msg_id = message_send(
        supply_user["token"], supply_channels["channel_id"], "Some message"
    )["message_id"]
    with pytest.raises(InputError):
        message_unreact(supply_user["token"], msg_id, 0)


def test_message_unreact_user_unjoined(supply_user):
    new_user = auth_register("owner@gmail.com", "Password", "Owner", "Name")
    channel_id = channels_create(new_user["token"], "Channel", True)["channel_id"]
    msg_id = message_send(new_user["token"], channel_id, "Some message")["message_id"]
    with pytest.raises(InputError):
        message_unreact(supply_user["token"], msg_id, 1)


def test_message_unreact_not_reacted(supply_user, supply_channels):
    msg_id = message_send(
        supply_user["token"], supply_channels["channel_id"], "Some message"
    )["message_id"]
    with pytest.raises(InputError):
        message_unreact(supply_user["token"], msg_id, 1)


def test_message_unreact_valid(supply_user, supply_channels):
    msg_id = message_send(
        supply_user["token"], supply_channels["channel_id"], "Some message"
    )["message_id"]
    message_react(supply_user["token"], msg_id, 1)
    message_unreact(supply_user["token"], msg_id, 1)
    with pytest.raises(InputError):
        message_unreact(supply_user["token"], msg_id, 1)


def test_message_pin_invalid_msg_id(supply_user):
    with pytest.raises(InputError):
        message_pin(supply_user["token"], -1)


def test_message_pin_user_unjoined(supply_user):
    new_user = auth_register("owner@gmail.com", "Password", "Owner", "Name")
    channel_id = channels_create(new_user["token"], "Channel", True)["channel_id"]
    msg_id = message_send(new_user["token"], channel_id, "Some message")["message_id"]
    with pytest.raises(AccessError):
        message_pin(supply_user["token"], msg_id)


def test_message_pin_valid(supply_user, supply_channels):
    msg_id = message_send(
        supply_user["token"], supply_channels["channel_id"], "Some message"
    )["message_id"]
    message_pin(supply_user["token"], msg_id)
    with pytest.raises(InputError):
        message_pin(supply_user["token"], msg_id)


def test_message_unpin_invalid_msg_id(supply_user, supply_channels):
    msg_id = message_send(
        supply_user["token"], supply_channels["channel_id"], "Some message"
    )["message_id"]
    with pytest.raises(InputError):
        message_unpin(supply_user["token"], msg_id + 1)


def test_message_unpin_user_unjoined(supply_user):
    new_user = auth_register("owner@gmail.com", "Password", "Owner", "Name")
    channel_id = channels_create(new_user["token"], "Channel", True)["channel_id"]
    msg_id = message_send(new_user["token"], channel_id, "Some message")["message_id"]
    with pytest.raises(AccessError):
        message_unpin(supply_user["token"], msg_id)


def test_message_unpin_not_owner(supply_user, supply_channels):
    new_user = auth_register("owner@gmail.com", "Password", "New", "User")
    channel_join(new_user["token"], supply_channels["channel_id"])
    msg_id = message_send(
        supply_user["token"], supply_channels["channel_id"], "Some message"
    )["message_id"]
    message_pin(supply_user["token"], msg_id)
    with pytest.raises(AccessError):
        message_unpin(new_user["token"], msg_id)


def test_message_unpin_valid(supply_user, supply_channels):
    msg_id = message_send(
        supply_user["token"], supply_channels["channel_id"], "Some message"
    )["message_id"]
    message_pin(supply_user["token"], msg_id)
    message_unpin(supply_user["token"], msg_id)
    with pytest.raises(InputError):
        message_unpin(supply_user["token"], msg_id)
