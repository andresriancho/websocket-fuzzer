from websocket_fuzzer.tokenizer.quotes import tokenize_double_quotes
from websocket_fuzzer.tokenizer.method_name import tokenize_method_name

TOKENIZER_METHODS = [
    tokenize_double_quotes,
    #tokenize_method_name
]


def create_tokenized_messages(original_message, ignore_tokens):
    tokenized_messages = []

    for tokenizer_method in TOKENIZER_METHODS:
        tokenized_messages.extend(tokenizer_method(original_message, ignore_tokens))

    return tokenized_messages
