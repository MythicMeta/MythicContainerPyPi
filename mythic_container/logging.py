import logging
import sys
from .config import settings
LOG_FORMAT = (
    "%(levelname) -4s %(asctime)s %(funcName) "
    "-3s %(lineno) -5d: %(message)s"
)
logger = logging.getLogger("mythic")


def initialize():
    settingLogLevel = settings.get("debug_level", "info")
    handler = logging.StreamHandler(sys.stdout)
    if settingLogLevel == "warning":
        logger.setLevel(logging.WARNING)
        handler.setLevel(logging.WARNING)
    elif settingLogLevel == "info":
        logger.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)
    elif settingLogLevel == "debug":
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
        handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info(f"[*] Using debug level: {settingLogLevel}")

