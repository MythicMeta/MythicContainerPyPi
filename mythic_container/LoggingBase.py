from collections.abc import Callable, Awaitable
from typing import Union

import mythic_container
from .logging import logger
import aiohttp
from .config import settings
import json

class NewCallbackLoggingData:
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

class LoggingMessage:
    Data: Union[dict | NewCallbackLoggingData | None]
    def __init__(self,
                 operation_id: int = None,
                 operation_name: str = None,
                 operator_username: str = None,
                 timestamp: str = None,
                 action: str = None,
                 data: dict = None,
                 **kwargs):
        self.OperationID = operation_id
        self.OperationName = operation_name
        self.OperatorUsername = operator_username
        self.Timestamp = timestamp
        self.Action = action
        if self.Action == mythic_container.LOG_TYPE_CALLBACK:
            self.Data = NewCallbackLoggingData(**data)
        else:
            self.Data = data
        for k,v in kwargs.items():
            logger.info(f"unknown kwarg {k} {v}")


class Log:

    new_callback: Callable[ [LoggingMessage], Awaitable[None] ] = None
    new_feedback: Callable[ [LoggingMessage], Awaitable[None] ] = None
    new_startup:  Callable[ [LoggingMessage], Awaitable[None] ] = None



