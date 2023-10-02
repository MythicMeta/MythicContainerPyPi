from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PushC2MessageFromAgent(_message.Message):
    __slots__ = ["Base64Message", "C2ProfileName", "Message", "RemoteIP", "TaskingSize"]
    BASE64MESSAGE_FIELD_NUMBER: _ClassVar[int]
    Base64Message: bytes
    C2PROFILENAME_FIELD_NUMBER: _ClassVar[int]
    C2ProfileName: str
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    Message: bytes
    REMOTEIP_FIELD_NUMBER: _ClassVar[int]
    RemoteIP: str
    TASKINGSIZE_FIELD_NUMBER: _ClassVar[int]
    TaskingSize: int
    def __init__(self, C2ProfileName: _Optional[str] = ..., RemoteIP: _Optional[str] = ..., TaskingSize: _Optional[int] = ..., Message: _Optional[bytes] = ..., Base64Message: _Optional[bytes] = ...) -> None: ...

class PushC2MessageFromMythic(_message.Message):
    __slots__ = ["Error", "Message", "Success"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    Error: str
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    Message: bytes
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    def __init__(self, Success: bool = ..., Error: _Optional[str] = ..., Message: _Optional[bytes] = ...) -> None: ...
