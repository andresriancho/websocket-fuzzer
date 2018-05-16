import unittest


from websocket_fuzzer.tokenizer.quotes import tokenize_double_quotes


class TestQuotesTokenizer(unittest.TestCase):
    def test_simple(self):
        message = '{"Maker":"BMW"}'
        expected = ['{"$TOKEN$":"BMW"}', '{"Maker":"$TOKEN$"}']
        generated = []

        for tokenized_message in tokenize_double_quotes(message):
            generated.append(tokenized_message)

        self.assertEqual(expected, generated)
