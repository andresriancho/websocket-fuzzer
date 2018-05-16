from websocket_fuzzer.tokenizer import TOKEN


def tokenize_method_name(ws_message, ignore_tokens):
    """
    If the web service message (string passed as parameter) is:

        auth/Login|{"username": "...", "password": "..."}

    This method will yield:

        $TOKEN$/Login|{"username": "...", "password": "..."}
        auth/$TOKEN$|{"username": "...", "password": "..."}

    This is useful for other parts of the tool which will replace the token with
    something interesting and send it to the remote websocket.

    :param ws_message: A string representing the message
    :return: Many modified messages
    """
    tokenized = []

    slash = ws_message.find('/')
    pipe = ws_message.find('|')

    if not slash:
        return tokenized

    if not pipe:
        return tokenized

    if pipe < slash:
        return tokenized

    group = ws_message[:slash]
    if group not in ignore_tokens:
        tokenized.append(TOKEN + ws_message[slash:])

    method = ws_message[slash:pipe]
    if method not in ignore_tokens:
        tokenized.append(ws_message[:slash + 1] + TOKEN + ws_message[pipe:])

    return tokenized
