from auth import auth_token
from data import data
from error import InputError, AccessError
from user import validate_user_id, find_user


def channel_invite(token, channel_id, u_id):
    """Invite a user to join a channel."""
    token_id = auth_token(token)
    validate_channel_id(channel_id)
    validate_user_id(u_id)

    channel = find_channel(channel_id)
    if token_id not in [
        member["u_id"] for member in channel["owner_members"]
    ] and token_id not in [member["u_id"] for member in channel["all_members"]]:
        raise AccessError("The authorised user is not a member of the channel.")

    user = find_user(u_id)
    user_details = {
        "u_id": user["u_id"],
        "name_first": user["name_first"],
        "name_last": user["name_last"],
    }
    channel["all_members"].append(user_details)
    return {}


def channel_details(token, channel_id):
    """Provide basic details about a channel."""
    u_id = auth_token(token)
    validate_channel_id(channel_id)

    channel = find_channel(channel_id)
    if u_id not in [
        member["u_id"] for member in channel["owner_members"]
    ] and u_id not in [member["u_id"] for member in channel["all_members"]]:
        raise AccessError("The authorised user is not a member of the channel.")

    channel_details = {
        "name": channel["name"],
        "owner_members": channel["owner_members"],
        "all_members": channel["all_members"],
    }
    return channel_details


def channel_messages(token, channel_id, start):
    """Return up to 50 messages from a channel."""
    u_id = auth_token(token)
    validate_channel_id(channel_id)

    messages = [
        message for message in data["messages"] if message["channel_id"] == channel_id
    ]
    num_messages = len(messages)
    if start > num_messages:
        raise InputError(
            "start is greater than the total number of messages in the channel."
        )

    channel = find_channel(channel_id)
    if u_id not in [
        member["u_id"] for member in channel["owner_members"]
    ] and u_id not in [member["u_id"] for member in channel["all_members"]]:
        raise AccessError("The authorised user is not a member of the channel.")

    messages = messages[::-1][start:][:50]
    end = start + 50 if num_messages - start >= 50 else -1
    return {
        "messages": messages,
        "start": start,
        "end": end,
    }


def channel_leave(token, channel_id):
    """Remove a user from a channel."""
    u_id = auth_token(token)
    validate_channel_id(channel_id)

    channel = find_channel(channel_id)
    if u_id in [member["u_id"] for member in channel["owner_members"]]:
        member = next(
            member for member in channel["owner_members"] if member["u_id"] == u_id
        )
        channel["owner_members"].remove(member)
    elif u_id in [member["u_id"] for member in channel["all_members"]]:
        member = next(
            member for member in channel["all_members"] if member["u_id"] == u_id
        )
        channel["all_members"].remove(member)
    else:
        raise AccessError("The authorised user is not a member of the channel.")

    return {}


def channel_join(token, channel_id):
    """Add a user to a channel."""
    u_id = auth_token(token)
    validate_channel_id(channel_id)

    user = find_user(u_id)
    channel = find_channel(channel_id)
    if not channel["is_public"] and user["permission_id"] != 1:
        raise AccessError("Channel ID is private. User cannot join.")

    member = {
        "u_id": user["u_id"],
        "name_first": user["name_first"],
        "name_last": user["name_last"],
    }
    channel["all_members"].append(member)

    return {}


def channel_addowner(token, channel_id, u_id):
    """Make a user an owner of a channel."""
    token_id = auth_token(token)
    validate_channel_id(channel_id)

    user = find_user(token_id)
    channel = find_channel(channel_id)
    owner_id_list = [owner["u_id"] for owner in channel["owner_members"]]
    if u_id in owner_id_list:
        raise InputError("User to be added is already an owner of the channel.")
    elif token_id not in owner_id_list and user["permission_id"] != 1:
        raise AccessError("Authorised user is not an owner of the channel.")

    new_owner = find_user(u_id)
    member = {
        "u_id": new_owner["u_id"],
        "name_first": new_owner["name_first"],
        "name_last": new_owner["name_last"],
    }
    channel["owner_members"].append(member)

    return {}


def channel_removeowner(token, channel_id, u_id):
    """Remove an owner of a channel."""
    token_id = auth_token(token)
    validate_channel_id(channel_id)

    user = find_user(token_id)
    channel = find_channel(channel_id)
    owner_id_list = [owner["u_id"] for owner in channel["owner_members"]]
    if u_id not in owner_id_list:
        raise InputError("User to be removed is not an owner of the channel.")
    elif token_id not in owner_id_list and user["permission_id"] != 1:
        raise AccessError("Authorised user is not an owner of the channel.")

    user = find_user(u_id)
    member = {
        "u_id": user["u_id"],
        "name_first": user["name_first"],
        "name_last": user["name_last"],
    }
    channel["owner_members"].remove(member)

    return {}


def validate_channel_id(channel_id):
    """Raise InputError if given an invalid channel id."""
    channel_id_list = [channel["channel_id"] for channel in data["channels"]]
    if channel_id not in channel_id_list:
        raise InputError("Channel ID does not exist.")


def find_channel(channel_id):
    """Find channel given channel_id."""
    return next(
        channel for channel in data["channels"] if channel["channel_id"] == channel_id
    )
