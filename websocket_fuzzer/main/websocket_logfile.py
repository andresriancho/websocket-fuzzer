class WebSocketLogFile(object):
    def __init__(self, log_path, log_filename):
        self.log_path = log_path
        self.log_filename = log_filename
        self.counter = 0

    def get_filename(self):
        return '%s/%s-%s.log' % (self.log_path, self.log_filename, self.counter)

    def write(self, message):
        filename = self.get_filename()
        self.counter += 1

        file(filename, 'w').write(message)
