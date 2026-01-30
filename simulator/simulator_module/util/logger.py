import sys

class Logger:

    def __init__(self, log_filename=None):
        if log_filename is not None:
            self.logfile = open(log_filename, "w")

    def log(self, *args):
        print(*args, file=sys.stderr)
        if self.logfile is not None:
            print(*args, file=self.logfile)
            self.logfile.flush()

    def close(self):
        if self.logfile is not None:
            self.logfile.close()
