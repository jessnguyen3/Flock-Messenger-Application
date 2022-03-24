""" File containing the functions clear(), users_all() and search()."""
from data import data
from auth import auth_token
from channels import channels_list
from error import AccessError, InputError
from user import validate_user_id, find_user
from data import data
from auth import auth_token
from channels import channels_list


def clear():
    """
    Clears all data stored in the project's data file.
    """
    data["id"] = 0
    data["users"][:] = []
    data["sessions"][:] = []
    data["messages"][:] = []
    data["channels"][:] = []


def users_all(token):
    """
    Return a list of dictionaries where each dictionary contains the user's u_id,
    email, name_first, name_last and handle_str.
    """
    auth_token(token)

    users = []
    for user in data["users"]:
        user_data = {
            "u_id": user["u_id"],
            "email": user["email"],
            "name_first": user["name_first"],
            "name_last": user["name_last"],
            "handle_str": user["handle_str"],
        }
        users.append(user_data)

    return {"users": users}


# Assumption: Upper and Lower case letters are viewed as the same, does not affect the search
def search(token, query_str):
    """
    Return a list of messages (matching the query string) in all of
    the channels the user has joined. In the list, each message is stored
    in a dictionary containing the message_id, u_id, message, time_created.
    """
    auth_token(token)
    # Create a list of channel_ids of channels the user is in
    channels = channels_list(token)["channels"]
    channel_ids = [channel["channel_id"] for channel in channels]
    messages = []

    for message in data["messages"]:
        if (
            query_str.lower() in message["message"].lower()
            and message["channel_id"] in channel_ids
        ):
            message_data = {
                "message_id": message["message_id"],
                "u_id": message["u_id"],
                "message": message["message"],
                "time_created": message["time_created"],
            }
            messages.append(message_data)
    return {"messages": messages}


def admin_userpermission_change(token, u_id, permission_id):
    token_id = auth_token(token)
    if find_user(token_id)["permission_id"] == 1:
        if permission_id in [1, 2]:
            validate_user_id(u_id)
            user = find_user(u_id)
            user["permission_id"] = permission_id
        else:
            raise InputError("permission_id is invalid.")
    else:
        raise AccessError("The authorised user is not an owner.")
