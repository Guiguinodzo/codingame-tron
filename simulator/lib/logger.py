import sys

class Logger:

    def __init__(self, log_filename):
        self.log_filename = log_filename
        self.logfile = open(log_filename, "w")

    def log(self, *args):
        print(*args, file=sys.stderr)
        print(*args, file=self.logfile)
        self.logfile.flush()

    def close(self):
        self.logfile.close()



