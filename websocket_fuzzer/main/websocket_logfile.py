import os


class WebSocketLogFile(object):
    def __init__(self, tokenized_count, log_path, log_filename):
        self.tokenized_count = tokenized_count
        self.log_path = log_path
        self.log_filename = log_filename
        self.counter = 0

        self.makedirs()

    def makedirs(self):
        output_path = '%s/%s/' % (self.log_path, self.tokenized_count)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

    def get_filename(self):
        return '%s/%s/%s-%s.log' % (self.log_path,
                                    self.tokenized_count,
                                    self.log_filename,
                                    self.counter)

    def write(self, message):
        filename = self.get_filename()
        self.counter += 1

        file(filename, 'w').write(message)
