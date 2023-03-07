from collections.abc import Callable, Awaitable
from typing import Union

import mythic_container
from .logging import logger
import aiohttp
from .config import settings
import json

class NewCallbackWebhookData:
    def __init__(self,
                 user: str = None,
                 host: str = None,
                 ips: str = None,
                 domain: str = None,
                 external_ip: str = None,
                 process_name: str = None,
                 pid: int = 0,
                 os: str = None,
                 architecture: str = None,
                 agent_type: str = None,
                 description: str = None,
                 extra_info: str = None,
                 sleep_info: str = None,
                 display_id: int = 0,
                 id: int = 0,
                 integrity_level: int = 2):
        self.User = user
        self.Host = host
        self.IPs = json.loads(ips) if ips is not None else None
        self.Domain = domain
        self.ExternalIP = external_ip
        self.ProcessName = process_name
        self.PID = pid
        self.Os = os
        self.Architecture = architecture
        self.AgentType = agent_type
        self.Description = description
        self.ExtraInfo = extra_info
        self.SleepInfo = sleep_info
        self.DisplayID = display_id
        self.ID = id
        self.IntegrityLevel = integrity_level
    def to_json(self):
        return {
            "user": self.User,
            "host": self.Host,
            "ips": self.IPs,
            "domain": self.Domain,
            "external_ip": self.ExternalIP,
            "process_name": self.ProcessName,
            "pid": self.PID,
            "os": self.Os,
            "architecture": self.Architecture,
            "description": self.Description,
            "extra_info": self.ExtraInfo,
            "sleep_info": self.SleepInfo,
            "display_id": self.DisplayID,
            "id": self.ID,
            "integrity_level": self.IntegrityLevel
        }
class NewFeedbackWebhookData:
    def __init__(self,
                 task_id: int = None,
                 display_id: int = None,
                 message: str = None,
                 feedback_type: str = None,
                 **kwargs):
        self.TaskID = task_id
        self.Message = message
        self.FeedbackType = feedback_type
        self.DisplayID = display_id
        for k,v in kwargs.items():
            logger.info(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "task_id": self.TaskID,
            "message": self.Message,
            "feedback_type": self.FeedbackType,
            "display_id": self.DisplayID
        }
class NewStartupWebhookData:
    def __init__(self,
                 startup_message: str = None,
                 **kwargs):
        self.StartupMessage = startup_message
        for k,v in kwargs.items():
            logger.info(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "startup_message": self.StartupMessage
        }
class WebookMessage:
    Data: Union[dict | NewCallbackWebhookData | NewFeedbackWebhookData | NewStartupWebhookData | None]
    def __init__(self,
                 operation_id: int = None,
                 operation_name: str = None,
                 operation_webhook: str = None,
                 operation_channel: str = None,
                 operator_username: str = None,
                 action: str = None,
                 data: dict = None,
                 **kwargs):
        self.OperationID = operation_id
        self.OperationName = operation_name
        self.OperationWebhook = operation_webhook
        self.OperationChannel = operation_channel
        self.OperatorUsername = operator_username
        self.Action = action
        if self.Action == mythic_container.WEBHOOK_TYPE_NEW_CALLBACK:
            self.Data = NewCallbackWebhookData(**data)
        elif self.Action == mythic_container.WEBHOOK_TYPE_NEW_FEEDBACK:
            self.Data = NewFeedbackWebhookData(**data)
        elif self.Action == mythic_container.WEBHOOK_TYPE_NEW_STARTUP:
            self.Data = NewStartupWebhookData(**data)
        else:
            self.Data = data
        for k,v in kwargs.items():
            logger.info(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "operation_id": self.OperationID,
            "operation_name": self.OperationName,
            "operation_webhook": self.OperationWebhook,
            "operation_channel": self.OperationChannel,
            "operator_username": self.OperatorUsername,
            "action": self.Action,
            "data": self.Data if isinstance(self.Data, dict) or self.Data is None else self.Data.to_json()
        }


class Webhook:
    webhook_url: str = None
    webhook_channel: str = None

    new_callback: Callable[ [WebookMessage], Awaitable[None] ] = None
    new_feedback: Callable[ [WebookMessage], Awaitable[None] ] = None
    new_startup:  Callable[ [WebookMessage], Awaitable[None] ] = None

    def getWebhookURL(self, inputMsg: WebookMessage) -> str:
        if inputMsg.OperationWebhook is not None and inputMsg.OperationWebhook != "":
            return inputMsg.OperationWebhook
        elif settings.get("webhook_default_url", None) is not None:
            return settings.get("webhook_default_url")
        elif self.webhook_url is not None:
            return self.webhook_url
        else:
            logger.error("")
            return ""

    def getWebhookChannel(self, inputMsg: WebookMessage) -> str:
        if inputMsg.OperationChannel is not None and inputMsg.OperationChannel != "":
            return inputMsg.OperationWebhook
        elif inputMsg.Action == mythic_container.WEBHOOK_TYPE_NEW_CALLBACK and settings.get("webhook_default_callback_channel", None) is not None:
            return settings.get("webhook_default_callback_channel")
        elif inputMsg.Action == mythic_container.WEBHOOK_TYPE_NEW_FEEDBACK and settings.get("webhook_default_feedback_channel", None) is not None:
            return settings.get("webhook_default_feedback_channel")
        elif inputMsg.Action == mythic_container.WEBHOOK_TYPE_NEW_STARTUP and settings.get("webhook_default_startup_channel", None) is not None:
            return settings.get("webhook_default_startup_channel")
        elif settings.get("webhook_default_channel", None) is not None:
            return settings.get("webhook_default_channel")
        elif self.webhook_channel is not None:
            return self.webhook_channel
        else:
            logger.error(f"No webhook channel found")
            return ""


async def sendWebhookMessage(contents: dict, url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=contents, ssl=False) as resp:
                if resp.status == 200:
                    responseData = await resp.text()
                    logger.debug(f"webhook response data: {responseData}")
                else:
                    logger.error(f"[-] Failed to send webhook message: {resp}")
    except Exception as e:
        logger.exception(f"[-] Failed to send webhook: {e}")
        return False

