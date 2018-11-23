# -*- coding: utf-8 -*-
import logging

from websocket_fuzzer.main.main import fuzz_websockets
from messages import *

#
#   Configure logging
#
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)-8s] %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='output.log',
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s][%(levelname)-8s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


#
#   User configured parameters
#

# The websocket address, including the protocol, for example:
#
#       ws://localhost
#       wss://localhost
#
ws_address = 'wss://ic2acts3.adobeconnect.adobe.com/'

# The proxy server used to send the messages. This is very useful
# for debugging the tools
http_proxy_host = 'localhost'
http_proxy_port = '8081'

# Log path, all messages are logged in different files
log_path = 'output/'

# Websocket authentication message. The tool will send the authentication
# message (if included in messages below) and wait for `session_active_message`
# before sending `message`


def generate_auth_message():
    #ticket = get_ticket()

    auth_message = {"type": "NCFunc",
                    "method": "connect",
                    "url": "rtmp://10.51.19.239:1935/?rtmp://localhost:8506/meetingas3app/31422/294318/",
                    "params": {"ticket": "1234",
                               "reconnection": False,
                               "swfUrl": "http://testconnect.corp.adobe.com/common/meetinghtml/index.html"}}

    auth_message = json.dumps(auth_message, indent=4)
    return auth_message


def generate_stream():
    #ns_id = random.randint(5000, 1000000)
    return '{"type":"NCFunc","method":"createNetStream","nsId":"1018"}'


session_active_message = 'NetConnection.Connect.Success'

# When fuzzing `message` ignore these tokens. The tokens are part of the original
# message which shouldn't be replaced with the payloads. For example, if the
# message is:
#
#   {"foo": "bar"}
#
# And the `ignore_tokens` list contains "bar", then the fuzzer is not going to
# send payloads in "bar" but it will in "foo".
ignore_tokens = ["type",
                 "NCFunc",
                 "method",
                 "connect",
                 "url",
                 "rtmp://10.51.19.239:1935/?rtmp://localhost:8506/meetingas3app/31422/294318/",
                 "params",
                 "ticket",
                 "reconnection",
                 "swfUrl",
                 "http://testconnect.corp.adobe.com/common/meetinghtml/index.html"]

# The list containing messages to be sent to the websocket. In some cases
# You need to send two or more messages to set a specific remote state, and
# then you send the attack
init_messages = []

# The messages to be fuzzed, these are sent in different websocket connections
# after sending the `init_messages`.
#
# Each message is fuzzed using `create_tokenized_messages`. This tokenizer
# function, together with `replace_token_in_json` needs to be customized
# if your websocket messages are NOT JSON.
original_messages = [generate_auth_message]

# When doing analysis of the websocket responses to try to identify exceptions
# and other errors, ignore these errors since they are common for the
# application under test
ignore_errors = []

#
#   Do not touch these lines
#
fuzz_websockets(ws_address,
                init_messages,
                original_messages,
                session_active_message,
                ignore_tokens,
                ignore_errors,
                log_path,
                http_proxy_host,
                http_proxy_port)
