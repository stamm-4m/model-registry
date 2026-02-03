import logging
import sys


def setup_logging():
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(levelname)s:%(name)s:%(message)s [func:%(funcName)s]"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
