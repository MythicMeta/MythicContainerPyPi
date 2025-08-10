import ujson
from .logging import logger
from .LoggingBase import *


async def new_callback(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, definedLogger in loggers.items():
            if definedLogger.new_callback is not None and callable(definedLogger.new_callback):
                await definedLogger.new_callback(LoggingMessage(**msgDict))
            else:
                logger.error("No valid function for new_callback from logger")
    except:
        logger.exception("Failed to execute new_callback log")


async def new_credential(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, definedLogger in loggers.items():
            if definedLogger.new_credential is not None and callable(definedLogger.new_credential):
                await definedLogger.new_credential(LoggingMessage(**msgDict))
            else:
                logger.error("No valid function for new_credential from logger")
    except:
        logger.exception("Failed to execute new_credential log")


async def new_keylog(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, definedLogger in loggers.items():
            if definedLogger.new_keylog is not None and callable(definedLogger.new_keylog):
                await definedLogger.new_keylog(LoggingMessage(**msgDict))
            else:
                logger.error("No valid function for new_keylog from logger")
    except:
        logger.exception("Failed to execute new_keylog log")


async def new_file(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, definedLogger in loggers.items():
            if definedLogger.new_file is not None and callable(definedLogger.new_file):
                await definedLogger.new_file(LoggingMessage(**msgDict))
            else:
                logger.error("No valid function for new_file from logger")
    except:
        logger.exception("Failed to execute new_file log")


async def new_payload(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, definedLogger in loggers.items():
            if definedLogger.new_payload is not None and callable(definedLogger.new_payload):
                await definedLogger.new_payload(LoggingMessage(**msgDict))
            else:
                logger.error("No valid function for new_payload from logger")
    except:
        logger.exception("Failed to execute new_payload log")


async def new_artifact(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, definedLogger in loggers.items():
            if definedLogger.new_artifact is not None and callable(definedLogger.new_artifact):
                await definedLogger.new_artifact(LoggingMessage(**msgDict))
            else:
                logger.error("No valid function for new_artifact from logger")
    except:
        logger.exception("Failed to execute new_artifact log:")


async def new_task(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, definedLogger in loggers.items():
            if definedLogger.new_task is not None and callable(definedLogger.new_task):
                await definedLogger.new_task(LoggingMessage(**msgDict))
            else:
                logger.error("No valid function for new_task from logger")
    except:
        logger.exception("Failed to execute new_task log")


async def new_response(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, definedLogger in loggers.items():
            if definedLogger.new_response is not None and callable(definedLogger.new_response):
                await definedLogger.new_response(LoggingMessage(**msgDict))
            else:
                logger.error("No valid function for new_response from logger")
    except:
        logger.exception("Failed to execute new_response log")
