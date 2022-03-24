import auth
import channel
import channels
import message
import user
import other
import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from error import InputError


def defaultHandler(err):
    response = err.get_response()
    print("response", err, err.get_response())
    response.data = dumps(
        {
            "code": err.code,
            "name": "System Error",
            "message": err.get_description(),
        }
    )
    response.content_type = "application/json"
    return response


APP = Flask(__name__)
CORS(APP)

APP.config["TRAP_HTTP_EXCEPTIONS"] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=["GET"])
def echo():
    data = request.args.get("data")
    if data == "echo":
        raise InputError(description='Cannot echo "echo"')
    return dumps({"data": data})


@APP.route("/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    return dumps(auth.auth_login(email, password))


@APP.route("/auth/logout", methods=["POST"])
def auth_logout():
    token = request.get_json()["token"]
    return dumps(auth.auth_logout(token))


@APP.route("/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    name_first = data["name_first"]
    name_last = data["name_last"]
    return dumps(auth.auth_register(email, password, name_first, name_last))


@APP.route("/channel/invite", methods=["POST"])
def channel_invite():
    data = request.get_json()
    token = data["token"]
    channel_id = data["channel_id"]
    u_id = data["u_id"]
    return dumps(channel.channel_invite(token, channel_id, u_id))


@APP.route("/channel/details", methods=["GET"])
def channel_details():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    return dumps(channel.channel_details(token, channel_id))


@APP.route("/channel/messages", methods=["GET"])
def channel_messages():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    start = int(request.args.get("start"))
    return dumps(channel.channel_messages(token, channel_id, start))


@APP.route("/channel/leave", methods=["POST"])
def channel_leave():
    data = request.get_json()
    token = data["token"]
    channel_id = data["channel_id"]
    return dumps(channel.channel_leave(token, channel_id))


@APP.route("/channel/join", methods=["POST"])
def channel_join():
    data = request.get_json()
    token = data["token"]
    channel_id = data["channel_id"]
    return dumps(channel.channel_join(token, channel_id))


@APP.route("/channel/addowner", methods=["POST"])
def channel_addowner():
    data = request.get_json()
    token = data["token"]
    channel_id = data["channel_id"]
    u_id = data["u_id"]
    return dumps(channel.channel_addowner(token, channel_id, u_id))


@APP.route("/channel/removeowner", methods=["POST"])
def channel_removeowner():
    data = request.get_json()
    token = data["token"]
    channel_id = data["channel_id"]
    u_id = data["u_id"]
    return dumps(channel.channel_removeowner(token, channel_id, u_id))


@APP.route("/channels/list", methods=["GET"])
def channels_list():
    token = request.args.get("token")
    return dumps(channels.channels_list(token))


@APP.route("/channels/listall", methods=["GET"])
def channels_listall():
    token = request.args.get("token")
    return dumps(channels.channels_listall(token))


@APP.route("/channels/create", methods=["POST"])
def channels_create():
    data = request.get_json()
    token = data["token"]
    name = data["name"]
    is_public = data["is_public"]
    return dumps(channels.channels_create(token, name, is_public))


@APP.route("/message/send", methods=["POST"])
def message_send():
    data = request.get_json()
    token = data["token"]
    channel_id = int(data["channel_id"])
    message_actual = data["message"]
    return dumps(message.message_send(token, channel_id, message_actual))


@APP.route("/message/remove", methods=["DELETE"])
def message_remove():
    data = request.get_json()
    token = data["token"]
    message_id = int(data["message_id"])
    return dumps(message.message_remove(token, message_id))


@APP.route("/message/edit", methods=["PUT"])
def message_edit():
    data = request.get_json()
    token = data["token"]
    message_id = int(data["message_id"])
    message_actual = data["message"]
    return dumps(message.message_edit(token, message_id, message_actual))


@APP.route("/message/sendlater", methods=["POST"])
def message_sendlater():
    data = request.get_json()
    token = data["token"]
    channel_id = int(data["channel_id"])
    message_actual = data["message"]
    time_sent = int(data["time_sent"])
    return dumps(
        message.message_sendlater(token, channel_id, message_actual, time_sent)
    )


@APP.route("/message/react", methods=["POST"])
def message_react():
    data = request.get_json()
    token = data["token"]
    message_id = int(data["message_id"])
    react_id = int(data["react_id"])
    return dumps(message.message_react(token, message_id, react_id))


@APP.route("/message/unreact", methods=["POST"])
def message_unreact():
    data = request.get_json()
    token = data["token"]
    message_id = int(data["message_id"])
    react_id = int(data["react_id"])
    return dumps(message.message_unreact(token, message_id, react_id))


@APP.route("/message/pin", methods=["POST"])
def message_pin():
    data = request.get_json()
    token = data["token"]
    message_id = int(data["message_id"])
    return dumps(message.message_pin(token, message_id))


@APP.route("/message/unpin", methods=["POST"])
def message_unpin():
    data = request.get_json()
    token = data["token"]
    message_id = int(data["message_id"])
    return dumps(message.message_unpin(token, message_id))


@APP.route("/user/profile", methods=["GET"])
def user_profile():
    token = request.args.get("token")
    u_id = int(request.args.get("u_id"))
    return dumps(user.user_profile(token, u_id))


@APP.route("/user/profile/setname", methods=["PUT"])
def user_profile_setname():
    data = request.get_json()
    token = data["token"]
    name_first = data["name_first"]
    name_last = data["name_last"]
    return dumps(user.user_profile_setname(token, name_first, name_last))


@APP.route("/user/profile/setemail", methods=["PUT"])
def user_profile_setemail():
    data = request.get_json()
    token = data["token"]
    email = data["email"]
    return dumps(user.user_profile_setemail(token, email))


@APP.route("/user/profile/sethandle", methods=["PUT"])
def user_profile_sethandle():
    data = request.get_json()
    token = data["token"]
    handle_str = data["handle_str"]
    return dumps(user.user_profile_sethandle(token, handle_str))


@APP.route("/users/all", methods=["GET"])
def users_all():
    token = request.args.get("token")
    return dumps(other.users_all(token))


@APP.route("/admin/userpermission/change", methods=["POST"])
def admin_userpermission_change():
    data = request.get_json()
    token = data["token"]
    u_id = data["u_id"]
    permission_id = data["permission_id"]
    return dumps(other.admin_userpermission_change(token, u_id, permission_id))


@APP.route("/search", methods=["GET"])
def search():
    token = request.args.get("token")
    query_str = request.args.get("query_str")
    return dumps(other.search(token, query_str))


@APP.route("/clear", methods=["DELETE"])
def clear():
    return dumps(other.clear())


if __name__ == "__main__":
    APP.run(port=0)  # Do not edit this port
