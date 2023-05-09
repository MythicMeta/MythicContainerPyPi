from collections.abc import Callable, Awaitable
from typing import Union

import mythic_container
from .logging import logger
import aiohttp
from .config import settings
import json


class NewCallbackWebhookData:
    """The base information about a new callback within Mythic

    Attributes:
        User (str): The user for the callback
        Host (str): The hostname for the callback (in all caps)
        IPs (list[str]): An array of IP addresses for the callback
        Domain (str): The domain for the callback
        ExternalIP (str): The external IP address for the callback (if known)
        ProcessName (str): The name of the process executing the callback
        PID (int): The Process Identifier for the callback
        OS (str): The operating system information reported back by the callback (not the same as the os you selected when building the payload)
        Architecture (str): The architecture of the process running the callback
        PayloadType (str): The name of the Payload Type for this callback
        Description (str): The description for the callback (defaults to the description for the associtated payload)
        ExtraInfo (str): Freeform additional text that can be set on the callback
        SleepInfo (str): Sleep information that can be stored as part of the callback (not implicitly set)
        DisplayID (int): The ID that the user sees when looking at the callback in Mythic's UI
        ID (int): The unique ID associated with this callback that can be used with RPC calls
        IntegrityLevel (int): The integrity level of this callback (mirrors Windows integrity levels with 0-5 range and 3+ is High integrity)

    """
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
        self.OS = os
        self.Architecture = architecture
        self.PayloadType = agent_type
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
            "os": self.OS,
            "architecture": self.Architecture,
            "description": self.Description,
            "extra_info": self.ExtraInfo,
            "sleep_info": self.SleepInfo,
            "display_id": self.DisplayID,
            "id": self.ID,
            "agent_type": self.PayloadType,
            "integrity_level": self.IntegrityLevel
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class NewFeedbackWebhookData:
    """The base definition for new feedback a user is providing about Mythic

    Attributes:
        TaskID (int): The ID of the task associated with this feedback (if provided) that can be used with RPC Calls
        Message (str): The feedback message
        FeedbackType (str): The type of feedback
        DisplayID (int): The display ID of the task that the user would see

    """
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
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "message": self.Message,
            "feedback_type": self.FeedbackType,
            "display_id": self.DisplayID
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class NewStartupWebhookData:
    """The base definition for a notification that Mythic started

    Attributes:
        StartupMessage (str): The message that Mythic started

    """
    def __init__(self,
                 startup_message: str = None,
                 **kwargs):
        self.StartupMessage = startup_message
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "startup_message": self.StartupMessage
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class NewAlertWebhookData:
    """The base definition for a notification that there was an alert generated

    Attributes:
        OperatorID (int): The unique ID of the operator that caused this message (if not Mythic)
        Message (str): The alert message
        Source (str): The source of the alert message
        Count (int): The number of times this entry has been seen
        Timestamp (str): When this alert was generated

    """
    def __init__(self,
                 operator_id: int = None,
                 message: str = None,
                 source: str = None,
                 count: int = None,
                 timestamp: str = None,
                 **kwargs):
        self.OperatorID = operator_id
        self.Message = message
        self.Source = source
        self.Count = count
        self.Timestamp = timestamp
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "operator_id": self.OperatorID,
            "message": self.Message,
            "source": self.Source,
            "count": self.Count,
            "timestamp": self.Timestamp
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class WebhookMessage:
    """The base definition for webhook message from Mythic

    Attributes:
        OperationID (int): The operation ID associated with this event
        OperationName (str): The name of the operation associated with this event
        OperationWebhook (str): If the operation has a configured webhook url, it's here
        OperationChannel (str): If the operation has a configured webhook channel, it's here
        OperatorUsername (str): The username of the operator that caused this webhook event
        Action (str): The kind of webhook message
        Data: The action-specific data
    """
    Data: Union[dict |
                NewCallbackWebhookData |
                NewFeedbackWebhookData |
                NewStartupWebhookData |
                NewAlertWebhookData |
                None]

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
        elif self.Action == mythic_container.WEBHOOK_TYPE_NEW_ALERT:
            self.Data = NewAlertWebhookData(**data)
        elif self.Action == mythic_container.WEBHOOK_TYPE_NEW_CUSTOM:
            self.Data = data
        else:
            self.Data = data
        for k, v in kwargs.items():
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

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class Webhook:
    """The base definition for a webhook service to accept webhook messages from Mythic

    In your functions, you can use the sendWebhookMessage function to send the webhook message.

    Attributes:
        webhook_url (str): Custom webhook url to use in case one isn't configured in Mythic
        webhook_channel (str): Custom webhook channel to use in case one isn't configured in Mythic

    Functions:
        new_callback:
            If you want to accept messages about new callbacks, implement this function
        new_feedback:
            If you want to accept messages about new feedback, implement this function
        new_startup:
            If you want to accept messages about Mythic starting, implement this function
        new_alert:
            If you want to accept messages about alert messages from Mythic's operation event log
        new_custom:
            If you want to accept messages that are custom made by scripting
        getWebhookURL:
            This will automatically determine the url to use by looking at the operation configuration, this class' configuration, and any env configurations
        getWebhookChannel:
            This will automatically determine the channel to use by look at the operation configuration, this class' configuartion, and any env configurations
    """
    webhook_url: str = ""
    webhook_channel: str = ""

    new_callback: Callable[[WebhookMessage], Awaitable[None]] = None
    new_feedback: Callable[[WebhookMessage], Awaitable[None]] = None
    new_startup: Callable[[WebhookMessage], Awaitable[None]] = None
    new_alert: Callable[[WebhookMessage], Awaitable[None]] = None
    new_custom: Callable[[WebhookMessage], Awaitable[None]] = None

    def getWebhookURL(self, inputMsg: WebhookMessage) -> str:
        if settings.get("webhook_default_url", "") != "":
            return settings.get("webhook_default_url")
        elif inputMsg.OperationWebhook is not None and inputMsg.OperationWebhook != "":
            return inputMsg.OperationWebhook
        elif self.webhook_url is not None:
            return self.webhook_url
        else:
            logger.error("")
            return ""

    def getWebhookChannel(self, inputMsg: WebhookMessage) -> str:
        if inputMsg.Action == mythic_container.WEBHOOK_TYPE_NEW_CALLBACK and settings.get(
                "webhook_default_callback_channel", "") != "":
            return settings.get("webhook_default_callback_channel")
        elif inputMsg.Action == mythic_container.WEBHOOK_TYPE_NEW_FEEDBACK and settings.get(
                "webhook_default_feedback_channel", "") != "":
            return settings.get("webhook_default_feedback_channel")
        elif inputMsg.Action == mythic_container.WEBHOOK_TYPE_NEW_STARTUP and settings.get(
                "webhook_default_startup_channel", "") != "":
            return settings.get("webhook_default_startup_channel")
        elif inputMsg.Action == mythic_container.WEBHOOK_TYPE_NEW_ALERT and settings.get(
                "webhook_default_alert_channel", "") != "":
            return settings.get("webhook_default_alert_channel")
        elif inputMsg.Action == mythic_container.WEBHOOK_TYPE_NEW_CUSTOM and settings.get(
                "webhook_default_custom_channel", "") != "":
            return settings.get("webhook_default_custom_channel")
        elif settings.get("webhook_default_channel", "") != "":
            return settings.get("webhook_default_channel")
        elif inputMsg.OperationChannel is not None and inputMsg.OperationChannel != "":
            return inputMsg.OperationChannel
        elif self.webhook_channel is not None:
            return self.webhook_channel
        else:
            logger.error(f"No webhook channel found")
            return ""


async def sendWebhookMessage(contents: dict, url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=contents, ssl=False) as resp:
                if resp.status == 200:
                    responseData = await resp.text()
                    logger.debug(f"webhook response data: {responseData}")
                    return responseData
                else:
                    logger.error(f"[-] Failed to send webhook message: {resp}")
                    return f"[-] Failed to send webhook message: {resp}"
    except Exception as e:
        logger.exception(f"[-] Failed to send webhook: {e}")
        return f"[-] Failed to send webhook: {e}"
