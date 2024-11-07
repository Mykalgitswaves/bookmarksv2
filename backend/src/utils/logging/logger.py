import atexit
import datetime as dt
import json
import logging
import logging.config
import logging.handlers
import pathlib

logger = logging.getLogger("my_app")  # __name__ is a common choice

def setup_logging():
    config_file = pathlib.Path("src/utils/logging/logging_config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)

def main():
    setup_logging()
    logging.basicConfig(level="INFO")
    logger.debug("debug message", extra={"x": "hello"})
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    
main()