import json
import time
from datetime import datetime

from flask import request
import zmq

from constants import ZMQ_HOST, ZMQ_PORT

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://%s:%s" % (ZMQ_HOST, ZMQ_PORT))

# key: token, value: expiration date
whitelist = {}


def verify_token():
    # retrieve the token from the header
    if "Authorization" not in request.headers:
        return False
    header = request.headers["Authorization"]
    if not header.startswith("Bearer ") or len(header) < 8:
        return False
    token = header[7:]

    # if the token is in the whitelist
    if token in whitelist:
        expiration = whitelist[token]
        # if the token has not expired, return it
        if not is_past(expiration):
            return token
        # otherwise remove it
        whitelist.pop(token)

    # send the verifying request to the token dealer
    token_req = {
        "action": "verify",
        "token": token
    }
    data = json.dumps(token_req).encode("utf-8")
    socket.send(data)
    token_res = json.loads(socket.recv().decode("utf-8"))

    # if the token is valid, save it and its expiration date in the whitelist
    valid = token_res["valid"]
    if valid:
        whitelist[token] = token_res["expiration"]

    return valid


def verify_token_async():
    return


def is_past(timestamp):
    expiration = datetime.fromtimestamp(timestamp)
    now = datetime.utcnow()
    return expiration < now
