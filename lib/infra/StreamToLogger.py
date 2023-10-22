import logging
import sys


# https://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logfilepath):
        self.setupLogger(logfilepath)
        self.logger = logging.getLogger('STDOUT')
        self.log_level = logging.INFO
        self.linebuf = ''

        sys.stdout = self

    def write_maxim(self, buf):
        sys.stdout.write("maxim " + buf.rstrip())

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def setupLogger(self, logfilepath):
        logging.basicConfig(
            level=logging.DEBUG,
            # format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
            format='%(asctime)s: %(message)s',
            filename=logfilepath,
            filemode='a'
        )
