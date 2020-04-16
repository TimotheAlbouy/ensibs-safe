from datetime import datetime
from threading import Thread

import zmq

from users_api_constants import ZMQ_HOST, ZMQ_PORT

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://%s:%s" % (ZMQ_HOST, ZMQ_PORT))

# key: username, value: (token, expiration date)
whitelist = {}


def sign_token(username):
    # if the username is in the whitelist
    if username in whitelist:
        token = whitelist[username][0]
        expiration = whitelist[username][1]
        # if the token has not expired, return it
        if not is_past(expiration):
            return token
        # otherwise, remove it
        whitelist.pop(username)

    # send the signing request to the token dealer
    token_req = {
        "action": "sign",
        "username": username
    }
    socket.send_json(token_req)
    if not socket.poll(1000):
        t = Thread(None, sign_token_parallel, None, (username,))
        t.start()
        return None
    token_res = socket.recv_json()

    # save the token and expiration date in the whitelist
    whitelist[username] = (token_res["token"], token_res["expiration"])

    return token_res["token"]


def sign_token_parallel(username):
    token_res = socket.recv_json()
    whitelist[username] = (token_res["token"], token_res["expiration"])


def is_past(timestamp):
    expiration = datetime.fromtimestamp(timestamp)
    now = datetime.utcnow()
    return expiration < now
