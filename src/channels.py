from auth import auth_token
from data import data
from error import InputError, AccessError
from user import find_user


def channels_list(token):
    """Return a list with all channels the user is in."""
    u_id = auth_token(token)
    channels = []
    for channel in data["channels"]:
        if (u_id in [member["u_id"] for member in channel["owner_members"]]) or (
            u_id in [member["u_id"] for member in channel["all_members"]]
        ):
            channels.append(channel)
    return {"channels": channels}


def channels_listall(token):
    """Return a list with all channels."""
    auth_token(token)
    return {"channels": data["channels"]}


def channels_create(token, name, is_public):
    """Create a new channel and return the channel_id."""
    u_id = auth_token(token)
    user = find_user(u_id)
    member = {
        "u_id": user["u_id"],
        "name_first": user["name_first"],
        "name_last": user["name_last"],
    }
    if len(name) > 20:
        raise InputError("Name is more than 20 characters long")
    channel_id = data["id"]
    data["channels"].append(
        {
            "channel_id": channel_id,
            "name": name,
            "is_public": is_public,
            "owner_members": [member],
            "all_members": [],
        }
    )
    data["id"] += 1
    return {"channel_id": channel_id}
