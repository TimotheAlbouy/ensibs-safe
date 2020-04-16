import json
from datetime import datetime

import zmq

from constants import ZMQ_HOST, ZMQ_PORT

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://%s:%s" % (ZMQ_HOST, ZMQ_PORT))

# key: username, value: (token, expiration date)
whitelist = {}


async def sign_token(username):
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
    data = json.dumps(token_req).encode("utf-8")
    socket.send(data)
    token_res = json.loads(socket.recv().decode("utf-8"))

    # save the token and expiration date in the whitelist
    whitelist[username] = (token_res["token"], token_res["expiration"])

    return token_res["token"]


def sign_token_async():
    return


def is_past(timestamp):
    expiration = datetime.fromtimestamp(timestamp)
    now = datetime.utcnow()
    return expiration < now
