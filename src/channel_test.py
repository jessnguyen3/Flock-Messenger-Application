import pytest
from channel import *
from error import InputError, AccessError
from data import data
from auth import auth_register
from channels import channels_create
from other import clear
from message import *


@pytest.fixture
def supply_owner():
    clear()
    return auth_register("owner@gmail.com", "Password#1", "First", "Last")


@pytest.fixture
def supply_user():
    return auth_register("user@gmail.com", "CompSci1##", "User", "One")


@pytest.fixture
def supply_user1():
    clear()
    return auth_register("validemail@gmail.com", "123abc!@#", "one", "user")


@pytest.fixture
def supply_user2():
    return auth_register("otheremail@gmail.com", "123abc!@#", "two", "user")


@pytest.fixture
def supply_channel(supply_user1, supply_user2):
    channel0 = channels_create(supply_user1["token"], "channel0", False)  # {channel_id}
    channel0_detail = channel_details(
        supply_user1["token"], channel0["channel_id"]
    )  # {name, owner_members, all_members}
    channel0_detail["channel_id"] = channel0["channel_id"]
    return channel0


@pytest.fixture
def supply_message(supply_user1, supply_user2, supply_channel):
    message_send(supply_user1["token"], supply_channel["channel_id"], "The first")
    channel0 = supply_channel
    return channel0


# -----------------------test channel_invite----------------------------
def test_channel_invite_exception1_with_invalid_channel_id(
    supply_user1, supply_user2, supply_channel
):
    with pytest.raises(InputError):
        channel_invite(
            supply_user1["token"], "a", supply_user2["u_id"]
        )  # invalid channel id


def test_channel_invite_exception2_with_invalid_u_id(
    supply_user1, supply_user2, supply_channel
):
    with pytest.raises(InputError):
        channel_invite(
            supply_user1["token"], supply_channel["channel_id"], "a"
        )  # invalid u_id


def test_channel_invite_exception3_with_unauthorised_user(
    supply_user1, supply_user2, supply_channel
):
    with pytest.raises(AccessError):
        channel_invite(
            supply_user2["token"], supply_channel["channel_id"], supply_user1["u_id"]
        )  # unauthorised user


# -----------------------test channel_details----------------------------
def test_channel_details_exception1_with_invalid_channel_id(
    supply_user1, supply_user2, supply_channel
):
    with pytest.raises(InputError):
        channel_details(supply_user1["token"], "a")  # invalid channel id


def test_channel_details_exception2_with_unauthorised_user(
    supply_user1, supply_user2, supply_channel
):
    with pytest.raises(AccessError):
        channel_details(
            supply_user2["token"], supply_channel["channel_id"]
        )  # unauthorised user


def test_channel_details(supply_user1, supply_user2, supply_channel):
    # return name(string) owner_members(list of dict) all_members(list of dict)
    details = channel_details(supply_user1["token"], supply_channel["channel_id"])
    assert len(details) == 3
    list_owner = [owner["u_id"] for owner in details["owner_members"]]
    list_all = [allmember["u_id"] for allmember in details["all_members"]]
    list_both = list_owner + list_all
    assert 0 in list_both

    # ---------------------test channel_messages----------------------------


def test_channel_messages(supply_user1, supply_user2, supply_channel, supply_message):

    messages = channel_messages(supply_user1["token"], supply_message["channel_id"], 0)
    assert len(messages) == 3


def test_channel_messages_inputerror1_with_invalid_channel_id(
    supply_user1, supply_user2, supply_channel, supply_message
):
    with pytest.raises(InputError):
        channel_messages(supply_user1["token"], "a", 0)  # invalid channel id


def test_channel_messages_inputerror1_with_invalid_start_value(
    supply_user1, supply_user2, supply_channel
):
    with pytest.raises(AccessError):
        channel_messages(
            supply_user2["token"], supply_channel["channel_id"], 0
        )  # unauthorised user


def test_channel_leave_inputerror(supply_user1, supply_user2, supply_channel):
    with pytest.raises(InputError):
        channel_leave(supply_user1["token"], "a")  # invalid channel id


def test_channel_leave_accesserror(supply_user1, supply_user2, supply_channel):
    with pytest.raises(AccessError):
        channel_leave(
            supply_user2["token"], supply_channel["channel_id"]
        )  # unauthorised user


# NOTE: To test invalid channel_id, we use negative int since channel_id always >= 0
# Testing function channel_join
# ==================================================================
def test_join_public_channel(supply_owner, supply_user):
    channel1 = channels_create(supply_owner["token"], "Channel1", True)
    channel_join(supply_user["token"], channel1["channel_id"])


def test_join_private_channel(supply_owner, supply_user):
    channel2 = channels_create(supply_owner["token"], "Channel2", False)
    with pytest.raises(AccessError):
        channel_join(supply_user["token"], channel2["channel_id"])


def test_join_invalid_channel_id(supply_owner, supply_user):
    with pytest.raises(InputError):
        channel_join(supply_user["token"], -1024)


# ==================================================================
# End of Tests for function channel_join


# Testing function channel_addowner
# ==================================================================
def test_addowner_valid(supply_owner, supply_user):
    channel3 = channels_create(supply_owner["token"], "Channel3", True)
    channel_addowner(supply_owner["token"], channel3["channel_id"], supply_user["u_id"])
    print(data)
    # If user has been added owner, this will raise an InputError
    with pytest.raises(InputError):
        channel_addowner(
            supply_owner["token"], channel3["channel_id"], supply_user["u_id"]
        )


def test_addowner_invalid_channel_id(supply_owner, supply_user):
    with pytest.raises(InputError):
        channel_addowner(supply_owner["token"], -1024, supply_user["u_id"])


# User to be added as owner is already an owner of the channel
def test_addowner_already_owner(supply_owner, supply_user):
    channel4 = channels_create(supply_owner["token"], "Channel4", True)
    with pytest.raises(InputError):
        channel_addowner(
            supply_owner["token"], channel4["channel_id"], supply_owner["u_id"]
        )


# Authorised user is not an owner of the channel or the Flockr
def test_addowner_not_owner(supply_owner, supply_user):
    channel5 = channels_create(supply_owner["token"], "Channel5", True)
    with pytest.raises(AccessError):
        channel_addowner(
            supply_user["token"], channel5["channel_id"], supply_user["u_id"]
        )


# ==================================================================
# End of Tests for function channel_addowner


# Testing function channel_removeowner
# ==================================================================
def test_removeowner_valid(supply_owner, supply_user):
    channel6 = channels_create(supply_owner["token"], "Channel6", True)
    channel_removeowner(
        supply_owner["token"], channel6["channel_id"], supply_owner["u_id"]
    )


def test_removeowner_invalid_channel_id(supply_owner, supply_user):
    with pytest.raises(InputError):
        channel_removeowner(supply_owner["token"], -1024, supply_user["u_id"])


# Authorised user is not an owner of the channel or the Flockr
def test_removeowner_not_owner(supply_owner, supply_user):
    channel7 = channels_create(supply_owner["token"], "Channel7", True)
    with pytest.raises(AccessError):
        print(data["channels"])
        channel_removeowner(
            supply_user["token"], channel7["channel_id"], supply_owner["u_id"]
        )


# ==================================================================
# End of Tests for function channel_removeowner
