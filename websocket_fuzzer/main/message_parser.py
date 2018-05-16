import os


def get_messages_from_disk(path):
    """
    Get all the websocket messages from disk.

    Each message should be in a different file.

    :param path: The path where files with messages are found
    :return: Yield messages read from disk
    """
    for entry in os.listdir(path):
        entry = os.path.join(path, entry)
        if os.path.isfile(entry):
            yield file(entry).read()
