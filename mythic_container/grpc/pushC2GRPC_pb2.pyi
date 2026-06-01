from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PushC2MessageFromAgent(_message.Message):
    __slots__ = ("C2ProfileName", "RemoteIP", "Message", "OuterUUID", "Base64Message", "TrackingID", "AgentDisconnected")
    C2PROFILENAME_FIELD_NUMBER: _ClassVar[int]
    REMOTEIP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OUTERUUID_FIELD_NUMBER: _ClassVar[int]
    BASE64MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRACKINGID_FIELD_NUMBER: _ClassVar[int]
    AGENTDISCONNECTED_FIELD_NUMBER: _ClassVar[int]
    C2ProfileName: str
    RemoteIP: str
    Message: bytes
    OuterUUID: str
    Base64Message: bytes
    TrackingID: str
    AgentDisconnected: bool
    def __init__(self, C2ProfileName: _Optional[str] = ..., RemoteIP: _Optional[str] = ..., Message: _Optional[bytes] = ..., OuterUUID: _Optional[str] = ..., Base64Message: _Optional[bytes] = ..., TrackingID: _Optional[str] = ..., AgentDisconnected: bool = ...) -> None: ...

class PushC2MessageFromMythic(_message.Message):
    __slots__ = ("Success", "Error", "Message", "TrackingID")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRACKINGID_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    Error: str
    Message: bytes
    TrackingID: str
    def __init__(self, Success: bool = ..., Error: _Optional[str] = ..., Message: _Optional[bytes] = ..., TrackingID: _Optional[str] = ...) -> None: ...
