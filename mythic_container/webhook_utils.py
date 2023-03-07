import ujson
from .logging import logger
from .WebhookBase import *


async def new_startup(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        webhookServices = Webhook.__subclasses__()
        for cls in webhookServices:
            webhook = cls()
            if webhook.new_startup is not None and callable(webhook.new_startup):
                await webhook.new_startup(WebookMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_startup from webhook")
    except Exception as e:
        logger.exception(f"Failed to execute new_startup webhook: {e}")


async def new_callback(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        webhookServices = Webhook.__subclasses__()
        for cls in webhookServices:
            webhook = cls()
            if webhook.new_callback is not None and callable(webhook.new_callback):
                await webhook.new_callback(WebookMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_callback from webhook")
    except Exception as e:
        logger.exception(f"Failed to execute new_callback webhook: {e}")


async def new_feedback(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        webhookServices = Webhook.__subclasses__()
        for cls in webhookServices:
            webhook = cls()
            if webhook.new_feedback is not None and callable(webhook.new_feedback):
                await webhook.new_feedback(WebookMessage(**msgDict))
            else:
                logger.error(f"No valid function for new_feedback from webhook")
    except Exception as e:
        logger.exception(f"Failed to execute new_feedback webhook: {e}")