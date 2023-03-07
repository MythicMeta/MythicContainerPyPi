from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CryptoKeysFormat(_message.Message):
    __slots__ = ["DecKey", "EncKey", "Value"]
    DECKEY_FIELD_NUMBER: _ClassVar[int]
    DecKey: bytes
    ENCKEY_FIELD_NUMBER: _ClassVar[int]
    EncKey: bytes
    VALUE_FIELD_NUMBER: _ClassVar[int]
    Value: str
    def __init__(self, EncKey: _Optional[bytes] = ..., DecKey: _Optional[bytes] = ..., Value: _Optional[str] = ...) -> None: ...

class TrCustomMessageToMythicC2FormatMessage(_message.Message):
    __slots__ = ["C2Name", "CryptoKeys", "Message", "MythicEncrypts", "TranslationContainerName", "UUID"]
    C2NAME_FIELD_NUMBER: _ClassVar[int]
    C2Name: str
    CRYPTOKEYS_FIELD_NUMBER: _ClassVar[int]
    CryptoKeys: _containers.RepeatedCompositeFieldContainer[CryptoKeysFormat]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MYTHICENCRYPTS_FIELD_NUMBER: _ClassVar[int]
    Message: bytes
    MythicEncrypts: bool
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    TranslationContainerName: str
    UUID: str
    UUID_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, TranslationContainerName: _Optional[str] = ..., C2Name: _Optional[str] = ..., Message: _Optional[bytes] = ..., UUID: _Optional[str] = ..., MythicEncrypts: bool = ..., CryptoKeys: _Optional[_Iterable[_Union[CryptoKeysFormat, _Mapping]]] = ...) -> None: ...

class TrCustomMessageToMythicC2FormatMessageResponse(_message.Message):
    __slots__ = ["Error", "Message", "Success", "TranslationContainerName"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    Error: str
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    Message: bytes
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    TranslationContainerName: str
    def __init__(self, Success: bool = ..., Error: _Optional[str] = ..., Message: _Optional[bytes] = ..., TranslationContainerName: _Optional[str] = ...) -> None: ...

class TrGenerateEncryptionKeysMessage(_message.Message):
    __slots__ = ["C2Name", "CryptoParamName", "CryptoParamValue", "TranslationContainerName"]
    C2NAME_FIELD_NUMBER: _ClassVar[int]
    C2Name: str
    CRYPTOPARAMNAME_FIELD_NUMBER: _ClassVar[int]
    CRYPTOPARAMVALUE_FIELD_NUMBER: _ClassVar[int]
    CryptoParamName: str
    CryptoParamValue: str
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    TranslationContainerName: str
    def __init__(self, TranslationContainerName: _Optional[str] = ..., C2Name: _Optional[str] = ..., CryptoParamValue: _Optional[str] = ..., CryptoParamName: _Optional[str] = ...) -> None: ...

class TrGenerateEncryptionKeysMessageResponse(_message.Message):
    __slots__ = ["DecryptionKey", "EncryptionKey", "Error", "Success", "TranslationContainerName"]
    DECRYPTIONKEY_FIELD_NUMBER: _ClassVar[int]
    DecryptionKey: bytes
    ENCRYPTIONKEY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    EncryptionKey: bytes
    Error: str
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    TranslationContainerName: str
    def __init__(self, Success: bool = ..., Error: _Optional[str] = ..., EncryptionKey: _Optional[bytes] = ..., DecryptionKey: _Optional[bytes] = ..., TranslationContainerName: _Optional[str] = ...) -> None: ...

class TrMythicC2ToCustomMessageFormatMessage(_message.Message):
    __slots__ = ["C2Name", "CryptoKeys", "Message", "MythicEncrypts", "TranslationContainerName", "UUID"]
    C2NAME_FIELD_NUMBER: _ClassVar[int]
    C2Name: str
    CRYPTOKEYS_FIELD_NUMBER: _ClassVar[int]
    CryptoKeys: _containers.RepeatedCompositeFieldContainer[CryptoKeysFormat]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MYTHICENCRYPTS_FIELD_NUMBER: _ClassVar[int]
    Message: bytes
    MythicEncrypts: bool
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    TranslationContainerName: str
    UUID: str
    UUID_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, TranslationContainerName: _Optional[str] = ..., C2Name: _Optional[str] = ..., Message: _Optional[bytes] = ..., UUID: _Optional[str] = ..., MythicEncrypts: bool = ..., CryptoKeys: _Optional[_Iterable[_Union[CryptoKeysFormat, _Mapping]]] = ...) -> None: ...

class TrMythicC2ToCustomMessageFormatMessageResponse(_message.Message):
    __slots__ = ["Error", "Message", "Success", "TranslationContainerName"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    Error: str
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    Message: bytes
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    TRANSLATIONCONTAINERNAME_FIELD_NUMBER: _ClassVar[int]
    TranslationContainerName: str
    def __init__(self, Success: bool = ..., Error: _Optional[str] = ..., Message: _Optional[bytes] = ..., TranslationContainerName: _Optional[str] = ...) -> None: ...
