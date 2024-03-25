from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PushC2MessageFromAgent(_message.Message):
    __slots__ = ["AgentDisconnected", "Base64Message", "C2ProfileName", "Message", "OuterUUID", "RemoteIP", "TrackingID"]
    AGENTDISCONNECTED_FIELD_NUMBER: _ClassVar[int]
    AgentDisconnected: bool
    BASE64MESSAGE_FIELD_NUMBER: _ClassVar[int]
    Base64Message: bytes
    C2PROFILENAME_FIELD_NUMBER: _ClassVar[int]
    C2ProfileName: str
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    Message: bytes
    OUTERUUID_FIELD_NUMBER: _ClassVar[int]
    OuterUUID: str
    REMOTEIP_FIELD_NUMBER: _ClassVar[int]
    RemoteIP: str
    TRACKINGID_FIELD_NUMBER: _ClassVar[int]
    TrackingID: str
    def __init__(self, C2ProfileName: _Optional[str] = ..., RemoteIP: _Optional[str] = ..., Message: _Optional[bytes] = ..., OuterUUID: _Optional[str] = ..., Base64Message: _Optional[bytes] = ..., TrackingID: _Optional[str] = ..., AgentDisconnected: bool = ...) -> None: ...

class PushC2MessageFromMythic(_message.Message):
    __slots__ = ["Error", "Message", "Success", "TrackingID"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    Error: str
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    Message: bytes
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    TRACKINGID_FIELD_NUMBER: _ClassVar[int]
    TrackingID: str
    def __init__(self, Success: bool = ..., Error: _Optional[str] = ..., Message: _Optional[bytes] = ..., TrackingID: _Optional[str] = ...) -> None: ...
