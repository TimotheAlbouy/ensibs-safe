import datetime
import json

import zmq
import jwt

from constants import JWT_SECRET, JWT_ISSUER, JWT_ALGO, ZMQ_PORT

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % ZMQ_PORT)


def sign(username):
    token = jwt.encode({
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iss": JWT_ISSUER,
        "sub": username
    }, JWT_SECRET, algorithm=JWT_ALGO).decode("utf-8")
    return token


def verify(token):
    try:
        # add admin claim?
        data = jwt.decode(token.encode("utf-8"), JWT_SECRET, issuer=JWT_ISSUER, algorithm=JWT_ALGO)
        return True, data["sub"]
    except jwt.InvalidTokenError:
        return False, None


def handle_request(data):
    # If the request payload is not a JSON object
    if type(data) is not dict:
        return {"error": "Invalid request"}

    # If the action parameter is not specified
    if "action" not in data:
        return {"error": "Missing action parameter"}

    # If it is a signing request
    if data["action"] == "sign":
        if "username" not in data:
            return {"error": "Missing username parameter"}
        token = sign(data["username"])
        return {"token": token}

    # If it is a verification request
    if data["action"] == "verify":
        if "token" not in data:
            return {"error": "Missing token parameter"}
        valid, username = verify(data["token"])
        ret = {"valid": valid}
        if valid:
            ret["username"] = username
        return ret

    # If the given action is incorrect
    return {"error": "Invalid action"}


if __name__ == "__main__":
    print("Token dealer running on port %s." % ZMQ_PORT)
    while True:
        # Wait for the next request from the client
        req = json.loads(socket.recv().decode("utf-8"))
        print("Received request:", req)
        # Send the response back to the client
        res = handle_request(req)
        socket.send(json.dumps(res).encode("utf-8"))
