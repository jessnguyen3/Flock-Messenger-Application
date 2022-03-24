"""
A test suite for  texting functions in file other.py .
The functions are users_all and search. 
"""

import pytest
from other import clear, search, users_all, admin_userpermission_change
from auth import auth_register
from channels import channels_create
from channel import channel_join
from message import message_send
from error import AccessError, InputError


@pytest.fixture
def supply_user1():
    """ Supply a user. """
    clear()
    return auth_register("validemail1@gmail.com", "Password1", "Valid", "Name")


@pytest.fixture
def supply_user2():
    """ Supply a second user. """
    return auth_register("jessn@gmail.com", "Comp1531", "Jess", "Nguyen")


# Testing the function users_all
# ===============================================================
def test_invalid_token():
    """ Testing that an invalid token (user is not authorised) throws an AccessError. """
    with pytest.raises(AccessError):
        users_all("INVALID_TOKEN")


def test_multiple_users(supply_user1, supply_user2):
    """ Testing that multiples users are stored in a list returned by function users_all. """
    users_list = users_all(supply_user1["token"])["users"]
    assert len(users_list) == 2

    # Check each users' email is in the list
    user_emails = [user["email"] for user in users_list]
    assert "validemail1@gmail.com" in user_emails
    assert "jessn@gmail.com" in user_emails

    # Check each users' u_id is in the list
    user_ids = [user["u_id"] for user in users_list]
    assert supply_user1["u_id"] in user_ids
    assert supply_user2["u_id"] in user_ids

    # Check each users' first name is in the list
    first_names = [user["name_first"] for user in users_list]
    assert "Valid" in first_names
    assert "Jess" in first_names

    # Check each users' last name is in the list
    last_names = [user["name_last"] for user in users_list]
    assert "Name" in last_names
    assert "Nguyen" in last_names


# ===============================================================


# Testing the function search
# ===============================================================
def test_search_invalid_token():
    """ Testing that invalid token raises an AccessError. """
    with pytest.raises(AccessError):
        search("INVALID_TOKEN", "some message")


def test_empty(supply_user1):
    """ Testing search function returns empty list if no messages have been sent."""
    assert search(supply_user1["token"], "A message")["messages"] == []


def test_no_messages(supply_user1):
    """ Testing search of messages without finding messages that match the query string."""
    channel_id = channels_create(supply_user1["token"], "channel", True)["channel_id"]

    message_send(supply_user1["token"], channel_id, "This is a message.")
    message_send(supply_user1["token"], channel_id, "Another message is here.")
    assert search(supply_user1["token"], "some string")["messages"] == []


def test_with_messages(supply_user1):
    """ Testing search of messages sent by only one user."""
    channel_id = channels_create(supply_user1["token"], "channel", True)["channel_id"]

    message_send(supply_user1["token"], channel_id, "This is a message.")
    message_send(supply_user1["token"], channel_id, "Another message is here.")
    message_send(supply_user1["token"], channel_id, "Last message.")
    message_send(supply_user1["token"], channel_id, "Okay maybe not.")
    messages_found = search(supply_user1["token"], "message")["messages"]
    assert len(messages_found) == 3

    messages = [message["message"] for message in messages_found]
    assert "This is a message." in messages
    assert "Another message is here." in messages
    assert "Last message." in messages

    u_ids = [message["u_id"] for message in messages_found]
    for u_id in u_ids:
        assert u_id == supply_user1["u_id"]  # only one user sent the messages


def test_with_uppercases(supply_user1):
    """
    Testing that the search function returns messages regardless if it is not
    exactly the same. That is, capital letters are irrelevant.
    For example, 'Message' is the same as 'message' and 'MESSAGE'.
    """
    channel_id = channels_create(supply_user1["token"], "channel", True)["channel_id"]
    message_send(supply_user1["token"], channel_id, "This is a Message.")
    message_send(supply_user1["token"], channel_id, "Another meSSage is here.")
    message_send(supply_user1["token"], channel_id, "Last message.")
    messages_found = search(supply_user1["token"], "Message")["messages"]
    assert len(messages_found) == 3

    messages = [message["message"] for message in messages_found]
    assert "This is a Message." in messages
    assert "Another meSSage is here." in messages
    assert "Last message." in messages

    u_ids = [message["u_id"] for message in messages_found]
    for u_id in u_ids:
        assert u_id == supply_user1["u_id"]  # only one user sent the messages


def test_search_with_multiple_users(supply_user1, supply_user2):
    """ Testing search function to find messages sent by multiple users. """

    channel_id = channels_create(supply_user1["token"], "channel", True)["channel_id"]
    channel_join(supply_user2["token"], channel_id)

    message_send(supply_user1["token"], channel_id, "This is a comp1531 subject.")
    message_send(
        supply_user1["token"], channel_id, "What COMP subject should I do next?."
    )
    message_send(supply_user1["token"], channel_id, "The term is CS not comp.")
    message_send(supply_user2["token"], channel_id, "Beep boop I am a robot.")
    message_send(supply_user2["token"], channel_id, "Robots are computerised beings.")
    message_send(supply_user2["token"], channel_id, "Hungry.")
    messages_found = search(supply_user1["token"], "comp")["messages"]
    assert len(messages_found) == 4

    messages = [message["message"] for message in messages_found]
    assert "This is a comp1531 subject." in messages
    assert "What COMP subject should I do next?." in messages
    assert "The term is CS not comp." in messages
    assert "Robots are computerised beings." in messages

    u_ids = [message["u_id"] for message in messages_found]
    assert supply_user1["u_id"] in u_ids
    assert supply_user2["u_id"] in u_ids


def test_messages_from_only_joined(supply_user1, supply_user2):
    """ Test that search function returns messages from only channel user has joined. """
    channel1 = channels_create(supply_user1["token"], "channel1", True)["channel_id"]
    channel2 = channels_create(supply_user2["token"], "channel2", True)["channel_id"]

    message_send(supply_user1["token"], channel1, "This is a comp1531 subject.")
    message_send(
        supply_user2["token"], channel2, "What COMP subject should I do next?."
    )
    message_send(supply_user2["token"], channel2, "The term is CS not comp.")
    message_send(supply_user2["token"], channel2, "Beep boop I am a robot.")

    messages_found = search(supply_user1["token"], "comp")["messages"]
    assert len(messages_found) == 1
    assert messages_found[0]["message"] == "This is a comp1531 subject."
    assert messages_found[0]["u_id"] == supply_user1["u_id"]


# ===============================================================

# Testing admin_userpermission_change
# ================================================================
def test_admin_invalid_token():
    """ Testing that invalid token raises an AccessError. """
    with pytest.raises(AccessError):
        admin_userpermission_change("INVALID_TOKEN", 1, 1)


def test_admin_invalid_uid(supply_user1):
    """ Testing that invalid u_id raises an InputError. """
    with pytest.raises(InputError):
        admin_userpermission_change(supply_user1["token"], supply_user1["u_id"] + 1, 1)


def test_admin_invalid_permission_value(supply_user1):
    """ Testing that invalid permission_id raises an InputError. """
    with pytest.raises(InputError):
        admin_userpermission_change(supply_user1["token"], supply_user1["u_id"], 3)


def test_admin_not_owner(supply_user1, supply_user2):
    """
    Testing that if the user (with token supplied) is not an owner, then an AccessError is raised.
    """
    with pytest.raises(AccessError):
        admin_userpermission_change(supply_user2["token"], supply_user1["u_id"], 2)


def test_admin_valid_inputs(supply_user1, supply_user2):
    """
    Testing that if the inputs are valid, then the permissions is changed.
    """
    admin_userpermission_change(supply_user1["token"], supply_user2["u_id"], 1)
    channel_id = channels_create(supply_user2["token"], "Test Channel", False)[
        "channel_id"
    ]
    channel_join(supply_user1["token"], channel_id)
