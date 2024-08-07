import logging
import logging.config
import json
import os

LOGS_DIR = os.path.join(os.path.dirname(__file__), "../logs")


def setup_logging():
    with open(os.path.join(os.path.dirname(__file__), "logging.json")) as f:
        config = json.load(f)
    logging.config.dictConfig(config)


def get_logger(name):
    return logging.getLogger(name)


os.makedirs(LOGS_DIR, exist_ok=True)

# Setup at import time to ensure all child processes have the same config
setup_logging()
