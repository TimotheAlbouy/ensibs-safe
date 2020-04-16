from datetime import datetime
from threading import Thread

from flask import request
import zmq

from safe_api_constants import ZMQ_HOST, ZMQ_PORT

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://%s:%s" % (ZMQ_HOST, ZMQ_PORT))

verify_token_errors = {
    400: "Authorization header missing or invalid",
    401: "Authentication failed",
    503: "Token dealer unavailable"
}

# key: token, value: expiration date
whitelist = {}


def verify_token():
    # retrieve the token from the header
    if "Authorization" not in request.headers:
        return 400
    header = request.headers["Authorization"]
    if not header.startswith("Bearer ") or len(header) < 8:
        return 400
    token = header[7:]

    # if the token is in the whitelist
    if token in whitelist:
        expiration = whitelist[token]
        # if the token has not expired, return that it is valid
        if not is_past(expiration):
            return 200
        # otherwise remove it
        whitelist.pop(token)

    # send the verifying request to the token dealer
    token_req = {
        "action": "verify",
        "token": token
    }
    socket.send_json(token_req)
    if not socket.poll(1000):
        t = Thread(None, verify_token_parallel, None, (token,))
        t.start()
        return 503
    token_res = socket.recv_json()

    # if the token is valid, save it and its expiration date in the whitelist
    valid = token_res["valid"]
    if valid:
        whitelist[token] = token_res["expiration"]

    return 200


def verify_token_parallel(token):
    token_res = socket.recv_json()
    whitelist[token] = token_res["expiration"]


def is_past(timestamp):
    expiration = datetime.fromtimestamp(timestamp)
    now = datetime.utcnow()
    return expiration < now
