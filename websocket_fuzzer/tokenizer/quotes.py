import re

from websocket_fuzzer.tokenizer import TOKEN

QUOTES_RE = re.compile('"(.*?)"')


def tokenize_double_quotes(ws_message, ignore_tokens):
    """
    If the web service message (string passed as parameter) is:

        GetFeatures|{"CustomerId":30001}|{"Maker":"BMW","RegionCode":"US"}

    This method will yield:

        GetFeatures|{"$TOKEN$":30001}|{"Maker":"BMW","RegionCode":"US"}
        GetFeatures|{"CustomerId":30001}|{"$TOKEN$":"BMW","RegionCode":"US"}
        GetFeatures|{"CustomerId":30001}|{"Maker":"$TOKEN$","RegionCode":"US"}
        GetFeatures|{"CustomerId":30001}|{"Maker":"BMW","$TOKEN$":"US"}
        GetFeatures|{"CustomerId":30001}|{"Maker":"BMW","RegionCode":"$TOKEN$"}

    This is useful for other parts of the tool which will replace the token with
    something interesting and send it to the remote websocket.

    :param ws_message: A string representing the message
    :return: Many modified messages
    """
    tokenized = []

    for match in QUOTES_RE.finditer(ws_message):
        start, end = match.span()

        should_tokenize = True

        for ignore_token in ignore_tokens:
            if ignore_token == ws_message[start + 1:end - 1]:
                should_tokenize = False
                break

        if not should_tokenize:
            continue

        tokenized.append(ws_message[:start + 1] + TOKEN + ws_message[end - 1:])

    return tokenized
