import time
import logging
from logging.handlers import TimedRotatingFileHandler

class FileHandler(TimedRotatingFileHandler):
    def __init__(self, fPath, fLevel=logging.DEBUG):
        super().__init__(fPath, when="D", interval=1, utc=True)
        self.setLevel = fLevel
        fmt = logging.Formatter(fmt="%(asctime)s - %(levelname)-8s - %(filename)s:%(funcName)s:%(lineno)s - %(message)s", datefmt="%y%m%d %H:%M:%S")
        fmt.converter = time.gmtime
        self.setFormatter(fmt)

class StreamHandler(logging.StreamHandler):
    def __init__(self, sLevel=logging.INFO):
        super().__init__()
        self.setLevel(sLevel)
        fmt = logging.Formatter(fmt="%(levelname)-8s - %(filename)s:%(funcName)s:%(lineno)s - %(message)s")
        self.setFormatter(fmt) 

