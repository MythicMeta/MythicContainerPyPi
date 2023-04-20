import ujson
from .logging import logger
from .LoggingBase import *


async def new_callback(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        loggingServices = Log.__subclasses__()
        for cls in loggingServices:
            definedLogger = cls()
            if definedLogger.new_callback is not None and callable(definedLogger.new_callback):
                await definedLogger.new_callback(LoggingMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_callback from logger")
    except Exception as e:
        logger.exception(f"Failed to execute new_callback log: {e}")


async def new_credential(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        loggingServices = Log.__subclasses__()
        for cls in loggingServices:
            definedLogger = cls()
            if definedLogger.new_credential is not None and callable(definedLogger.new_credential):
                await definedLogger.new_credential(LoggingMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_credential from logger")
    except Exception as e:
        logger.exception(f"Failed to execute new_credential log: {e}")


async def new_keylog(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        loggingServices = Log.__subclasses__()
        for cls in loggingServices:
            definedLogger = cls()
            if definedLogger.new_keylog is not None and callable(definedLogger.new_keylog):
                await definedLogger.new_keylog(LoggingMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_keylog from logger")
    except Exception as e:
        logger.exception(f"Failed to execute new_keylog log: {e}")


async def new_file(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        loggingServices = Log.__subclasses__()
        for cls in loggingServices:
            definedLogger = cls()
            if definedLogger.new_file is not None and callable(definedLogger.new_file):
                await definedLogger.new_file(LoggingMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_file from logger")
    except Exception as e:
        logger.exception(f"Failed to execute new_file log: {e}")


async def new_payload(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        loggingServices = Log.__subclasses__()
        for cls in loggingServices:
            definedLogger = cls()
            if definedLogger.new_payload is not None and callable(definedLogger.new_payload):
                await definedLogger.new_payload(LoggingMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_payload from logger")
    except Exception as e:
        logger.exception(f"Failed to execute new_payload log: {e}")


async def new_artifact(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        loggingServices = Log.__subclasses__()
        for cls in loggingServices:
            definedLogger = cls()
            if definedLogger.new_artifact is not None and callable(definedLogger.new_artifact):
                await definedLogger.new_artifact(LoggingMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_artifact from logger")
    except Exception as e:
        logger.exception(f"Failed to execute new_artifact log: {e}")


async def new_task(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        loggingServices = Log.__subclasses__()
        for cls in loggingServices:
            definedLogger = cls()
            if definedLogger.new_task is not None and callable(definedLogger.new_task):
                await definedLogger.new_task(LoggingMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_task from logger")
    except Exception as e:
        logger.exception(f"Failed to execute new_task log: {e}")
