import time
import threading
from auth import auth_token
from channel import find_channel, validate_channel_id
from data import data
from error import InputError, AccessError
from user import find_user
from channels import channels_list


def message_send(token, channel_id, message):
    """Send a message to the channel specified by channel_id."""
    validate_channel_id(
        channel_id
    )  # assumption, channel id is validated in message_send
    u_id = auth_token(token)
    if len(message) > 1000:
        raise InputError("Message is longer than 1000 characters.")
    channel = find_channel(channel_id)
    if u_id not in (
        [owner["u_id"] for owner in channel["owner_members"]]
        + [member["u_id"] for member in channel["all_members"]]
    ):
        raise AccessError(f"User is not a member of channel {channel_id}.")
    message_id = data["id"]
    message_details = {
        "channel_id": channel_id,
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_created": int(time.time()),
        "reacts": [],
        "is_pinned": False,
    }
    data["id"] += 1
    data["messages"].append(message_details)
    return {"message_id": message_id}


def message_remove(token, message_id):
    """Remove the message specified by message_id."""
    u_id = auth_token(token)
    if not any(message["message_id"] == message_id for message in data["messages"]):
        raise InputError("Message with that id no longer exists.")
    message = find_message(message_id)
    check_user_message_perms(u_id, message)
    data["messages"].remove(message)
    return {}


def message_edit(token, message_id, message):
    """Update content of message specified by message_id."""
    u_id = auth_token(token)
    message_details = find_message(message_id)
    check_user_message_perms(u_id, message_details)
    if message:
        message_idx = data["messages"].index(message_details)
        data["messages"][message_idx]["message"] = message
    else:
        message_remove(token, message_id)
    return {}


def message_sendlater(token, channel_id, message, time_sent):
    time_now = int(time.time())
    print(time_now)
    print(time_sent)
    if time_sent < time_now:
        raise InputError("Time given is not valid - it is in the past.")
    # schedule the time
    t = threading.Timer(
        time_sent - time_now, message_send, [token, channel_id, message]
    )
    t.start()
    return {}


def message_react(token, message_id, react_id):
    react_exceptions(token, message_id, react_id, True)
    u_id = auth_token(token)
    find_message(message_id)["reacts"][0]["u_ids"].append(u_id)
    return {}


def message_unreact(token, message_id, react_id):
    react_exceptions(token, message_id, react_id, False)
    u_id = auth_token(token)
    find_message(message_id)["reacts"][0]["u_ids"].remove(u_id)
    return {}


def message_pin(token, message_id):
    pin_exceptions(token, message_id, True)
    find_message(message_id)["is_pinned"] = True
    return {}


def message_unpin(token, message_id):
    pin_exceptions(token, message_id, False)
    find_message(message_id)["is_pinned"] = False
    return {}


def react_exceptions(token, message_id, react_id, reacting):
    if react_id != 1:
        raise InputError("The react ID is invalid. Only valid react ID is 1.")

    # A list of user's channel ids
    channel_ids = [
        channel["channel_id"] for channel in channels_list(token)["channels"]
    ]
    message = find_message(message_id)
    if message["channel_id"] not in channel_ids:
        raise InputError(
            "The message_id is not a valid message within a channel user has joined."
        )

    u_id = auth_token(token)
    message = find_message(message_id)
    # Exceptions related to no reacts at all
    if message["reacts"] == []:
        if reacting:
            react_info = {"react_id": react_id, "u_ids": []}
            message["reacts"].append(react_info)
        else:
            raise InputError("Message has no reacts.")  # an assumption made here

    # Exceptions related to user already reacted/unreacted to the message
    if u_id in message["reacts"][0]["u_ids"] and reacting:
        raise InputError("User is currently reacted to the message.")
    elif u_id not in message["reacts"][0]["u_ids"] and not reacting:
        raise InputError("User is not currently reacted to the message.")


def pin_exceptions(token, message_id, pinning):
    message = find_message(message_id)
    channels = channels_list(token)["channels"]
    # A list of user's channel ids
    channel_ids = [channel["channel_id"] for channel in channels]
    if not message:
        raise InputError("Message ID given is not a valid message.")
    elif message["channel_id"] not in channel_ids:
        raise AccessError("User is not part of channel the message is in.")

    # Exceptions related to whether the msg is already pinned/unpinned
    if not message["is_pinned"] and not pinning:
        raise InputError("Message is already unpinned.")
    elif message["is_pinned"] and pinning:
        raise InputError("Message is already pinned.")

    u_id = auth_token(token)
    permission_id = find_user(u_id)["permission_id"]
    message_channel = find_channel(message["channel_id"])
    owners = [owner["u_id"] for owner in message_channel["owner_members"]]
    if u_id not in owners and permission_id != 1:
        raise AccessError("User is not an owner.")


def check_user_message_perms(u_id, message):
    """Raise AccessError if user is lacks perms to modify a message."""
    if message["u_id"] != u_id:
        channel = find_channel(message["channel_id"])
        if (
            not any(owner["u_id"] == u_id for owner in channel["owner_members"])
            and find_user(u_id)["permission_id"] != 1
        ):
            raise AccessError(
                "Authorised user is not permitted \
                              to edit this message."
            )


def find_message(message_id):
    """Find message given message_id."""
    return next(
        (
            message
            for message in data["messages"]
            if message["message_id"] == message_id
        ),
        False,
    )
