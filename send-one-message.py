# -*- coding: utf-8 -*-
import logging

from websocket_fuzzer.main.websocket_wrapper import send_payloads_in_websocket

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
ws_address = ''

# The proxy server used to send the messages. This is very useful
# for debugging the tools
http_proxy_host = 'localhost'
http_proxy_port = '8080'

# Log path, all messages are logged in different files
log_path = 'output/'

# Websocket authentication message. The tool will send the authentication
# message (if included in messages below) and wait for `session_active_message`
# before sending `message`
auth_message = ''
session_active_message = ''

# The message to send to the websocket
message = ''

# The list containing all messages to be sent to the websocket. In some cases
# You need to send two or more messages to set a specific remote state, and
# then you send the attack
messages = [
    auth_message,
    message,
]

# When doing analysis of the websocket responses to try to identify exceptions
# and other errors, ignore these errors since they are common for the
# application under test
ignore_errors = []

#
#   Do not touch these lines
#
send_payloads_in_websocket(ws_address,
                           messages,
                           session_active_message,
                           ignore_errors,
                           0,
                           log_path,
                           http_proxy_host,
                           http_proxy_port)
