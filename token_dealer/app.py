import datetime

import zmq
import jwt

from token_dealer_constants import JWT_SECRET, JWT_ISSUER, JWT_ALGO, ZMQ_HOST, ZMQ_PORT

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://%s:%s" % (ZMQ_HOST, ZMQ_PORT))


def sign(username):
    iat = datetime.datetime.utcnow()
    exp = iat + datetime.timedelta(hours=1)
    token = jwt.encode({
        "iat": iat,
        "exp": exp,
        "iss": JWT_ISSUER,
        "sub": username
    }, JWT_SECRET, algorithm=JWT_ALGO).decode("utf-8")
    return token, datetime.datetime.timestamp(exp)


def verify(token):
    try:
        # add admin claim?
        data = jwt.decode(token.encode("utf-8"), JWT_SECRET, issuer=JWT_ISSUER, algorithm=JWT_ALGO)
        return True, data["sub"], data["iat"]
    except jwt.InvalidTokenError:
        return False, None, None


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
        token, expiration = sign(data["username"])
        return {"token": token, "expiration": expiration}

    # If it is a verification request
    if data["action"] == "verify":
        if "token" not in data:
            return {"error": "Missing token parameter"}
        valid, username, expiration = verify(data["token"])
        ret = {"valid": valid}
        if valid:
            ret["username"] = username
            ret["expiration"] = expiration
        return ret

    # If the given action is incorrect
    return {"error": "Invalid action"}


if __name__ == "__main__":
    print("Token dealer listening on %s:%s." % (ZMQ_HOST, ZMQ_PORT))
    while True:
        # Wait for the next request from the client
        req = socket.recv_json()
        print("Received request:", req)
        # Send the response back to the client
        res = handle_request(req)
        print("Sent response:", res)
        socket.send_json(res)
