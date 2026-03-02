import logging
import sys

FORMAT = "%(asctime)s.%(msecs)03d | %(levelname)s | %(name)s | %(jobId)s | %(message)s"
DATEFMT="%Y-%m-%d %H:%M:%S"

def setup(serviceName: str, logLevel=logging.INFO)->logging.Logger:


    log = logging.getLogger(serviceName)
    log.setLevel(logLevel)

    formatter = logging.Formatter(FORMAT, datefmt=DATEFMT)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    log.addHandler(handler)
    return log
