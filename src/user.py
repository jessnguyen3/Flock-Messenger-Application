"""
Functions related to the user's profile: allows user to display user_profile,
    edit their own profile (set name, email and handle)
"""
from auth import auth_token, validate_email
from data import data
from error import AccessError, InputError


def user_profile(token, u_id):
    """Displays a user's profile"""
    auth_token(token)
    validate_user_id(u_id)
    user = find_user(u_id)
    profile = {
        item: user[item] for item in user if item not in ("password", "permission_id")
    }
    return profile


def user_profile_setname(token, name_first, name_last):
    """Allows a user to set their first and last names"""
    u_id = auth_token(token)
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("First name must be between 1 and 50 characters long.")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Last name must be between 1 and 50 characters long.")
    user = find_user(u_id)
    user["name_first"] = name_first
    user["name_last"] = name_last
    return {}


def user_profile_setemail(token, email):
    """Allows a user to set their email"""
    u_id = auth_token(token)
    user = find_user(u_id)
    validate_email(email)
    for user in data["users"]:
        if user["email"] == email:
            raise InputError("Email is in use.")
    user["email"] = email
    return {}


def user_profile_sethandle(token, handle_str):
    """Allows a user to set their handle"""
    u_id = auth_token(token)
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError("Handle must be between 3 and 20 characters.")
    for user in data["users"]:
        if user["handle_str"] == handle_str:
            raise InputError("Handle is in use.")
    user = find_user(u_id)
    user["handle_str"] = handle_str
    return {}


def validate_user_id(u_id):
    """Checks if a given u_id corresponds to an existing user"""
    if u_id not in [user["u_id"] for user in data["users"]]:
        raise InputError("User with u_id is not a valid user")


def find_user(u_id):
    """Finds a user given u_id."""
    return next(user for user in data["users"] if user["u_id"] == u_id)
