import re
from data import data
from error import InputError, AccessError
import hashlib
import jwt

SECRET = "9tag7ubijkvN"


def auth_login(email, password):
    """Allow registered user to log in with correct email/pass combination,
    generates a token unique to the user"""
    validate_email(email)
    password = hashlib.sha256(password.encode()).hexdigest()
    for user in data["users"]:
        if user["email"] == email and user["password"] == password:
            token = jwt.encode(
                {"u_id": user["u_id"]}, SECRET, algorithm="HS256"
            ).decode("utf-8")
            data["sessions"].append({"token": token})
            return {"u_id": user["u_id"], "token": token}
        else:
            raise InputError("Email/Pass combination incorrect")


def auth_logout(token):
    """"Remove user with token from active sessions, logging them out"""
    init_len = len(data["sessions"])
    data["sessions"] = [
        active for active in data["sessions"] if not (active["token"] == token)
    ]
    if len(data["sessions"]) == init_len:
        return {"is_success": False}
    return {"is_success": True}


def auth_register(email, password, name_first, name_last):
    """Register a user with the given information, logins in the user"""
    # check if names are valid
    if (
        not name_first.isalpha()
        or not name_last.isalpha()
        or len(name_first) > 50
        or len(name_last) > 50
    ):

        raise InputError("Name is invalid")

    # email must be valid & not in use
    validate_email(email)
    for user in data["users"]:
        if user["email"] == email:
            raise InputError("Email is invalid")
    if len(password) < 6:
        raise InputError("Password is invalid")

    permission_id = 1 if not data["users"] else 2
    data["users"].append(
        {
            "u_id": data["id"],
            "email": email,
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "name_first": name_first,
            "name_last": name_last,
            "handle_str": generate_handle(name_first),
            "permission_id": permission_id,
        }
    )
    u_id = data["id"]
    token = jwt.encode({"u_id": u_id}, SECRET, algorithm="HS256").decode("utf-8")
    data["sessions"].append({"token": token})
    data["id"] += 1
    return {"u_id": u_id, "token": token}


def generate_handle(name):
    """Generate a unique handle given a user's first name"""
    name = name[:20]
    name = name.lower()
    i = 0
    while handle_exists(name):
        name = name[: (20 - len(str(i)))]
        name += str(i)
        i += 1
    return name


def handle_exists(name):
    """Check if the name given exists as a user string"""
    for user in data["users"]:
        if user["handle_str"] == name:
            return True
    return False


def validate_email(email):
    """Check to see if email is valid"""
    regex = "^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w+$"
    if not (re.search(regex, email)):
        raise InputError("Invalid email.")


def auth_token(token):
    """Check if token corresponds to valid user"""
    if token in [session["token"] for session in data["sessions"]]:
        return jwt.decode(token.encode("utf-8"), SECRET, algorithms=["HS256"])["u_id"]
    raise AccessError("Invalid token.")
