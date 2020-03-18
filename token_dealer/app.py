from datetime import datetime
from token_dealer.constants import SECRET

import zmq
import jwt
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    req = socket.recv()

    try:
        req_message = req.decode()
        print("Received request: %s" % req_message)
        req_data = json.load(req_message)

        if req_data.action == "sign":
            username = req_data.username
            token = jwt.encode({
                "exp": datetime.utcnow()
            }, SECRET)
            res_data = {
                "token": token
            }

        elif req_data.action == "verify":
            token = req_data.token
            res_data = {
                "correct"
            }

        else:
            res_data = None

    except jwt.ExpiredSignatureError:
        res_data = {
            "error": "Invalid JWT"
        }

    #  Send response back to client
    res_message = json.dumps(res_data)
    res = res_message.encode()
    socket.send(res)
