import websocket
import logging
import time
import ssl
import threading
import random
import string
import json

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter
from termcolor import colored

from websocket import WebSocketConnectionClosedException
from websocket_fuzzer.analysis.response_analyzer import analyze_response
from websocket_fuzzer.main.websocket_logfile import WebSocketLogFile

OUTGOING = 'outgoing'
INCOMING = 'incoming'


class FuzzingApp(websocket.WebSocketApp):
    def __init__(self, ws_address, messages_to_send, ignore_errors, tokenized_count,
                 log_path, session_active_message, *args, **kwargs):

        # Just ignore the kwargs passed as parameter and use ours:
        kwargs = {'on_message': self.on_message,
                  'on_error': self.on_error,
                  'on_close': self.on_close,
                  'on_open': self.on_open}

        super(FuzzingApp, self).__init__(ws_address, **kwargs)

        self._id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self._id = self._id.lower()

        log_filename = self._id
        self.log_file = WebSocketLogFile(tokenized_count, log_path, log_filename)

        self.messages_to_send = messages_to_send
        self.messages_pending_response = 0
        self.analyze_responses = False
        self.wait_for_active_session = False
        self.session_active_message = session_active_message
        self.latest_message_timestamp = None
        self.latest_message_sent_timestamp = None
        self.ignore_errors = ignore_errors

    def log(self, message, direction=None):
        self.log_file.write(self.json_indent(message))

        if direction in (OUTGOING, INCOMING):
            if self.latest_message_timestamp is None:
                relative_timestamp = 0.0
            else:
                relative_timestamp = time.time() - self.latest_message_timestamp
            self.latest_message_timestamp = time.time()

            message = self.json_highlight(message)

            if direction == OUTGOING:
                logging.debug('(%.4f)(%s)%s %s' % (relative_timestamp, self._id, colored('>>>', 'green'), message))
            elif direction == INCOMING:
                logging.debug('(%.4f)(%s)%s %s' % (relative_timestamp, self._id, colored('<<<', 'red'), message))
        else:
            logging.debug('(%s) %s' % (self._id, message))

    def json_highlight(self, message):
        try:
            json_object = json.loads(message)
        except:
            return message
        else:
            json_str = json.dumps(json_object, indent=4, sort_keys=True)
            highlighted = highlight(json_str, JsonLexer(), TerminalFormatter())
            return highlighted + '\n\n'

    def json_indent(self, message):
        """
        If the message is JSON, then print it with indents.

        Also add a trailing \n if required.

        :param message: The message sent/received by the websocket
        :return: A pretty version of the message
        """
        try:
            json_object = json.loads(message)
        except:
            return message
        else:
            json_str = json.dumps(json_object, indent=4, sort_keys=True)
            return json_str + '\n\n'

    def send_message(self, message, analyze=False):
        self.log(message, direction=OUTGOING)
        self.messages_pending_response += 1
        self.analyze_responses = analyze
        self.latest_message_sent_timestamp = time.time()

        try:
            self.send(message)
        except WebSocketConnectionClosedException:
            msg = '(%s) Connection was closed when trying to send message'
            logging.error(msg % self._id)

    def on_message(self, ws_conn, message):
        self.messages_pending_response = max(self.messages_pending_response - 1, 0)
        self.log(message, direction=INCOMING)

        if self.analyze_responses:
            found_interesting = analyze_response(message, self.ignore_errors)
            if found_interesting:
                msg = 'Potential issue found in connection with ID %s: %s'
                logging.warning(msg % (self._id, message))

        if self.session_active_message is not None:
            if self.session_active_message in message:
                self.wait_for_active_session = False

    def on_error(self, ws_conn, error):
        self.log('/error %s' % error)

    def on_close(self, ws_conn):
        self.log('/closed')

    def serialize_message(self, message):
        """
        This method gives the fuzzer support for using functions as messages.
        The function will be called to generate the message.

        :param message: A string with the message, or a function that generates
                        the message to send to the wire.

        :return: A string with the message
        """
        if callable(message):
            return message()

        return message

    def get_first_message(self):
        return self.serialize_message(self.messages_to_send[0])

    def iterate_all_messages_except_first(self):
        for message in self.messages_to_send[1:]:
            yield self.serialize_message(message)

    def on_open(self, ws_conn):
        logging.debug('Connection success!')

        self.send_message(self.get_first_message())

        t = threading.Thread(target=self.wait_for_login_and_send_payload,)
        t.start()

    def wait_for_pending_messages(self, wait_for_active_session=False):
        start_timestamp = time.time()
        should_wait = self.messages_pending_response > 0
        self.wait_for_active_session = wait_for_active_session

        while should_wait:
            # logging.debug('Waiting for server answers...')
            time.sleep(0.1)

            spent_time = time.time() - start_timestamp
            if spent_time > 5:
                logging.debug('Timed out waiting for answers')
                break

            if self.wait_for_active_session:
                continue

            waited_since_last_sent_message = time.time() - self.latest_message_sent_timestamp
            if waited_since_last_sent_message < 2.0:
                continue

            if self.messages_pending_response == 0:
                break

    def wait_for_login_and_send_payload(self):
        # This waits for the login response
        wait_for_active_session = self.session_active_message is not None
        self.wait_for_pending_messages(wait_for_active_session=wait_for_active_session)

        for message in self.iterate_all_messages_except_first():
            # Send the payload(s)
            self.send_message(message, analyze=True)

            # Wait for the payload response
            self.wait_for_pending_messages()

        # All done, close the connection!
        logging.debug('All answers received! Closing connection.')

        try:
            self.close()
        except:
            pass


def send_payloads_in_websocket(ws_address, messages_to_send, session_active_message,
                               ignore_errors, tokenized_count, log_path,
                               http_proxy_host, http_proxy_port):

    ws = FuzzingApp(ws_address,
                    messages_to_send,
                    ignore_errors,
                    tokenized_count,
                    log_path,
                    session_active_message)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE},
                   http_proxy_host=http_proxy_host,
                   http_proxy_port=http_proxy_port)
