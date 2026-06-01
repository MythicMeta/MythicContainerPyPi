from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TrCustomMessageToMythicC2FormatMessage(_message.Message):
    __slots__ = ("TranslationContainerName", "C2Name", "Message", "UUID", "MythicEncrypts", "CryptoKeys", "AuthContext")
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    C2NAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    MYTHICENCRYPTS_FIELD_NUMBER: _ClassVar[int]
    CRYPTOKEYS_FIELD_NUMBER: _ClassVar[int]
    AUTHCONTEXT_FIELD_NUMBER: _ClassVar[int]
    TranslationContainerName: str
    C2Name: str
    Message: bytes
    UUID: str
    MythicEncrypts: bool
    CryptoKeys: _containers.RepeatedCompositeFieldContainer[CryptoKeysFormat]
    AuthContext: str
    def __init__(self, TranslationContainerName: _Optional[str] = ..., C2Name: _Optional[str] = ..., Message: _Optional[bytes] = ..., UUID: _Optional[str] = ..., MythicEncrypts: bool = ..., CryptoKeys: _Optional[_Iterable[_Union[CryptoKeysFormat, _Mapping]]] = ..., AuthContext: _Optional[str] = ...) -> None: ...

class CryptoKeysFormat(_message.Message):
    __slots__ = ("EncKey", "DecKey", "Value", "Location")
    ENCKEY_FIELD_NUMBER: _ClassVar[int]
    DECKEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    EncKey: bytes
    DecKey: bytes
    Value: str
    Location: str
    def __init__(self, EncKey: _Optional[bytes] = ..., DecKey: _Optional[bytes] = ..., Value: _Optional[str] = ..., Location: _Optional[str] = ...) -> None: ...

class TrCustomMessageToMythicC2FormatMessageResponse(_message.Message):
    __slots__ = ("Success", "Error", "Message", "TranslationContainerName", "AuthContext")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTHCONTEXT_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    Error: str
    Message: bytes
    TranslationContainerName: str
    AuthContext: str
    def __init__(self, Success: bool = ..., Error: _Optional[str] = ..., Message: _Optional[bytes] = ..., TranslationContainerName: _Optional[str] = ..., AuthContext: _Optional[str] = ...) -> None: ...

class TrMythicC2ToCustomMessageFormatMessage(_message.Message):
    __slots__ = ("TranslationContainerName", "C2Name", "Message", "UUID", "MythicEncrypts", "CryptoKeys", "AuthContext")
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    C2NAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    MYTHICENCRYPTS_FIELD_NUMBER: _ClassVar[int]
    CRYPTOKEYS_FIELD_NUMBER: _ClassVar[int]
    AUTHCONTEXT_FIELD_NUMBER: _ClassVar[int]
    TranslationContainerName: str
    C2Name: str
    Message: bytes
    UUID: str
    MythicEncrypts: bool
    CryptoKeys: _containers.RepeatedCompositeFieldContainer[CryptoKeysFormat]
    AuthContext: str
    def __init__(self, TranslationContainerName: _Optional[str] = ..., C2Name: _Optional[str] = ..., Message: _Optional[bytes] = ..., UUID: _Optional[str] = ..., MythicEncrypts: bool = ..., CryptoKeys: _Optional[_Iterable[_Union[CryptoKeysFormat, _Mapping]]] = ..., AuthContext: _Optional[str] = ...) -> None: ...

class TrMythicC2ToCustomMessageFormatMessageResponse(_message.Message):
    __slots__ = ("Success", "Error", "Message", "TranslationContainerName", "AuthContext")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTHCONTEXT_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    Error: str
    Message: bytes
    TranslationContainerName: str
    AuthContext: str
    def __init__(self, Success: bool = ..., Error: _Optional[str] = ..., Message: _Optional[bytes] = ..., TranslationContainerName: _Optional[str] = ..., AuthContext: _Optional[str] = ...) -> None: ...

class TrGenerateEncryptionKeysMessage(_message.Message):
    __slots__ = ("TranslationContainerName", "C2Name", "CryptoParamValue", "CryptoParamName", "AuthContext")
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    C2NAME_FIELD_NUMBER: _ClassVar[int]
    CRYPTOPARAMVALUE_FIELD_NUMBER: _ClassVar[int]
    CRYPTOPARAMNAME_FIELD_NUMBER: _ClassVar[int]
    AUTHCONTEXT_FIELD_NUMBER: _ClassVar[int]
    TranslationContainerName: str
    C2Name: str
    CryptoParamValue: str
    CryptoParamName: str
    AuthContext: str
    def __init__(self, TranslationContainerName: _Optional[str] = ..., C2Name: _Optional[str] = ..., CryptoParamValue: _Optional[str] = ..., CryptoParamName: _Optional[str] = ..., AuthContext: _Optional[str] = ...) -> None: ...

class TrGenerateEncryptionKeysMessageResponse(_message.Message):
    __slots__ = ("Success", "Error", "EncryptionKey", "DecryptionKey", "TranslationContainerName", "AuthContext")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTIONKEY_FIELD_NUMBER: _ClassVar[int]
    DECRYPTIONKEY_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTHCONTEXT_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    Error: str
    EncryptionKey: bytes
    DecryptionKey: bytes
    TranslationContainerName: str
    AuthContext: str
    def __init__(self, Success: bool = ..., Error: _Optional[str] = ..., EncryptionKey: _Optional[bytes] = ..., DecryptionKey: _Optional[bytes] = ..., TranslationContainerName: _Optional[str] = ..., AuthContext: _Optional[str] = ...) -> None: ...
