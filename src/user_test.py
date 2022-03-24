"""Tests for all functions in user.py"""
import pytest
from user import (
    user_profile,
    user_profile_setemail,
    user_profile_sethandle,
    user_profile_setname,
)
from error import InputError, AccessError
from other import clear
from auth import auth_register


@pytest.fixture
def supply_user():
    """Clears any existing data and registers one user"""
    clear()
    return auth_register("validmail@mail.com", "password", "name", "lastname")


@pytest.fixture
def supply_user2():
    """Registers a second user"""
    return auth_register("alsomail@mail.com", "password", "New", "User")


def test_user_profile_nonexistent(supply_user):
    """InputError when u_id not registered doesnt exist"""
    with pytest.raises(InputError):
        user_profile(supply_user["token"], 3)


def test_user_profile_token(supply_user):
    """AccessError when fed invalid token"""
    with pytest.raises(AccessError):
        user_profile("3", 0)


def test_user_profile_success(supply_user):
    """user_profile works as intended given correct input."""
    assert user_profile(supply_user["token"], supply_user["u_id"]) == {
        "u_id": 0,
        "email": "validmail@mail.com",
        "name_first": "name",
        "name_last": "lastname",
        "handle_str": "name",
    }


# ============================================================================#
def test_user_profile_setname_invalid_name(supply_user):
    """Invalid first name or last name"""
    name = "a" * 100
    with pytest.raises(InputError):
        user_profile_setname(supply_user["token"], name, "Last")
    with pytest.raises(InputError):
        user_profile_setname(supply_user["token"], "First", name)


def test_user_profile_setname_pass(supply_user):
    """user_profile_setname works as intended given correct input."""
    user_profile_setname(supply_user["token"], "First", "Last")
    assert user_profile(supply_user["token"], supply_user["u_id"]) == {
        "u_id": 0,
        "email": "validmail@mail.com",
        "name_first": "First",
        "name_last": "Last",
        "handle_str": "name",
    }


def test_user_profile_setname_invalid_user(supply_user):
    """Invalid token supplied"""
    with pytest.raises(AccessError):
        user_profile_setname("2", "First", "Last")


# ============================================================================#
def test_user_profile_setemail_invalid_email(supply_user, supply_user2):
    """InputError when invalid email is supplied"""
    with pytest.raises(InputError):
        user_profile_setemail(supply_user["token"], "11111mailcom@@@@")
    with pytest.raises(InputError):
        user_profile_setemail(supply_user["token"], "alsomail@mail.com")


def test_user_profile_setemail_access_error(supply_user):
    """AccessError when invalid token is supplied"""
    with pytest.raises(AccessError):
        user_profile_setemail("3", "mail@mail.com")


def test_user_profile_setemail_pass(supply_user):
    """setemail works as intended given correct input."""
    user_profile_setemail(supply_user["token"], "newmail@mail.com")
    assert user_profile(supply_user["token"], supply_user["u_id"]) == {
        "u_id": 0,
        "email": "newmail@mail.com",
        "name_first": "name",
        "name_last": "lastname",
        "handle_str": "name",
    }


# ============================================================================#
def test_user_profile_sethandle_input_error_name(supply_user, supply_user2):
    """Handle noncomplaint with length requirements"""
    handle = "h" * 100
    with pytest.raises(InputError):
        user_profile_sethandle(supply_user["token"], handle)
    """Handle in use"""
    with pytest.raises(InputError):
        user_profile_sethandle(supply_user2["token"], "")


def test_user_profile_sethandle_pass(supply_user):
    """sethandle works as intended given correct input."""
    user_profile_sethandle(supply_user["token"], "newhandle")
    assert user_profile(supply_user["token"], supply_user["u_id"]) == {
        "u_id": 0,
        "email": "validmail@mail.com",
        "name_first": "name",
        "name_last": "lastname",
        "handle_str": "newhandle",
    }


def test_user_profile_sethandle_input_error(supply_user, supply_user2):
    """sethandle InputError when fed handle that is in user."""
    with pytest.raises(InputError):
        user_profile_sethandle(supply_user2["token"], "name")


def test_user_profile_sethandle_access_error(supply_user):
    """sethandle AccessError when fed invalid token."""
    with pytest.raises(AccessError):
        user_profile_sethandle("3", "validHandle")
