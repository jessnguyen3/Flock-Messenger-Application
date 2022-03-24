import pytest
from auth import auth_register, auth_login, auth_logout
from error import InputError
from other import clear


@pytest.fixture
def reset():
    clear()


@pytest.fixture
def supply_user():
    return auth_register("person1@mail.com", "password", "Person", "One")


def test_auth_register(reset):
    # check if you are allowed to register - pass
    auth_register("person1@mail.com", "password", "Person", "One")


def test_auth_register_inputerror_email(reset, supply_user):
    # email is invalid - fail
    with pytest.raises(InputError):
        auth_register("fakemail.com", "password", "fak3n4m3", "12345")
    # email is in use - fail
    with pytest.raises(InputError):
        auth_register("person1@mail.com", "password", "Person", "One")


def test_auth_register_inputerror_pass(reset):
    # password too short, fail
    with pytest.raises(InputError):
        auth_register("shortPass@mail.com", "pwrd", "Short", "Pass")


def test_auth_register_inputerror_names(reset):
    # password too short, fail
    with pytest.raises(InputError):
        auth_register("shortPass@mail.com", "pwrd", "Short", "Pass")
    # first name too short/long
    with pytest.raises(InputError):
        auth_register("noname@mail.com", "password", "", "LastName")
    with pytest.raises(InputError):
        auth_register("noname@mail.com", "password", "a" * 100, "LastName")
    # last name too short/long
    with pytest.raises(InputError):
        auth_register("noname@mail.com", "password", "FirstName", "")
    with pytest.raises(InputError):
        auth_register("noname@mail.com", "password", "FirstName", "a" * 100)
    # name has nums - fail
    with pytest.raises(InputError):
        auth_register("badname@mail.com", "password", "fak3n4m3", "12345")


# ==============================================================================================================#


def test_auth_login(reset, supply_user):
    # valid input - log in
    auth_logout(supply_user["token"])
    assert auth_login("person1@mail.com", "password") == supply_user


def test_auth_login_inputerror(reset, supply_user):
    # email not in database - no login
    with pytest.raises(InputError):
        auth_login("fakeuser@mail.com", "password")
    # wrong password - no login
    with pytest.raises(InputError):
        auth_login("person1@mail.com", "fakepass")


# ==============================================================================================================#


def test_auth_logout(reset, supply_user):
    # valid logout
    assert auth_logout(supply_user["token"]) == {"is_success": True}


def test_auth_logout_wrong_token(reset, supply_user):
    # incorrect token
    assert auth_logout("10") == {"is_success": False}
