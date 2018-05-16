import logging
import Queue

from concurrent import futures
from progress.bar import Bar

from websocket_fuzzer.main.websocket_wrapper import send_payloads_in_websocket
from websocket_fuzzer.tokenizer import TOKEN
from websocket_fuzzer.tokenizer.tokenizer import create_tokenized_messages


PAYLOADS = 'websocket_fuzzer/payloads/payloads.txt'


class ThreadPoolExecutorWithQueueSizeLimit(futures.ThreadPoolExecutor):
    def __init__(self, maxsize=50, *args, **kwargs):
        super(ThreadPoolExecutorWithQueueSizeLimit, self).__init__(*args, **kwargs)
        self._work_queue = Queue.Queue(maxsize=maxsize)


def fuzz_websockets(ws_address, init_messages, original_messages, session_active_message,
                    ignore_tokens, ignore_errors, output, http_proxy_host, http_proxy_port):
    """
    Creates a websocket connection, sends the payloads, writes output to disk.

    :param ws_address: The websocket address to connect and send messages to

    :param init_messages: The login messages to send before any payloads
    :param session_active_message: Wait for this message after sending the init_messages. Usually
                                   This is the message that says: "Login successful". Use None if
                                   there are no messages to wait for.

    :param original_messages: The original messages to be fuzzed

    :param ignore_tokens: When generating messages with payloads, do not replace these parts
                          of the message. In general you want to set this list to all the
                          keys in the json objects. For example, if the json object looks like
                          {"foo": "bar"} , and you only want to fuzz the "bar" part of the message
                          set ignore_tokens to ["foo"]

    :param ignore_errors: Ignore these errors when they are returned by the application

    :param output: Save all messages here

    :param http_proxy_host: The HTTP host (None if proxy shouldn't be used)
    :param http_proxy_port: The HTTP proxy (None if proxy shouldn't be used)

    :return: None
    """
    logging.info('Starting the fuzzing process...')
    payload_count = len(file(PAYLOADS).readlines())

    with ThreadPoolExecutorWithQueueSizeLimit(max_workers=25) as ex:

        for original_message in original_messages:

            logging.info('Fuzzing message: %s' % original_message)
            tokenized_messages = create_tokenized_messages(original_message, ignore_tokens)

            bar = Bar('Processing', max=len(tokenized_messages) * payload_count)

            for tokenized_message in tokenized_messages:

                for payload in file(PAYLOADS):

                    bar.next()

                    # You might want to modify this if the message is not JSON
                    modified_message = replace_token_in_json(payload, tokenized_message)

                    logging.debug('Generated fuzzed message: %s' % modified_message)

                    messages_to_send = init_messages[:]
                    messages_to_send.append(modified_message)

                    ex.submit(send_payloads_in_websocket,
                              ws_address, messages_to_send, session_active_message,
                              ignore_errors, output, http_proxy_host, http_proxy_port)

            bar.finish()

    logging.debug('Finished fuzzing process')


def replace_token_in_json(payload, tokenized_message):
    # Escape any quotes which are in the payload
    payload = payload.strip()
    payload = payload.replace('"', '\\"')

    # Do the replace
    modified_message = tokenized_message.replace(TOKEN, payload)
    return modified_message
