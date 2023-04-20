from collections.abc import Callable, Awaitable
from typing import Union

import mythic_container
from .logging import logger
import base64
import json
from .MythicCommandBase import PTTaskMessageTaskData


class NewCallbackLoggingData:
    """The base information about a new callback within Mythic

    Attributes:
        ID (int): The unique ID of the callback within Mythic, this is used for various RPC calls.
        DisplayID (int): The numerically increasing ID of a callback that's shown to the user in the Mythic UI.
        AgentCallbackID (str): The UUID of a callback that's sent down to a callback.
        InitCallback (str): The time of the initial callback
        LastCheckin (str): The time of the last time the callback checked in
        User (str): The user associated with the callback
        Host (str): The hostname for the callback (always in all caps)
        PID (int): The PID of the callback
        IP (str): The string representation of the IP array for the callback
        IPs (list[str]): An array of the IPs for the callback
        ExternalIp (str): The external IP address (if identified) for the callback
        ProcessName (str): The name of the process for the callback
        Description (str): The description for the callback (by default it matches the description for the associated payload)
        OperatorID (int): The ID of the operator that created the associated payload
        Active (bool): Indicating if this callback is in the active callbacks table or not
        IntegrityLevel (int): The integrity level for the callback that mirrors that of Windows (0-4) with a value of 3+ indicating a High Integrity (or root) callback
        Locked (bool): Indicating if this callback is locked or not so that other operators can't task it
        OperationID (int): The ID of the operation this callback belongs to
        CryptoType (str): The type of cryptography used for this callback (typically None or aes256_hmac)
        DecKey (bytes): The decryption key for this callback
        EncKey (bytes): The encryption key for this callback
        OS (str): The OS information reported back by the callback (not the same as the payload os you selected when building the agent)
        Architecture (str): The architecture of the process where this callback is executing
        Domain (str): The domain associated with the callback if there is one
        ExtraInfo (str): Freeform field of extra data that can be stored and retrieved with a callback
        SleepInfo (str): Freeform sleep information that can be stored and retrieved as part of a callback (this isn't pre-populated, the agent or command files must set it)
        RegisteredPayloadID (int): The unique ID for the payload associated with this callback
        LockedOperatorID (int): The unique ID for the operator that locked this callback (if it's locked)
        Timestamp (str): The timestamp for the last time this callback updated
    """
    def __init__(self,
                 id: int = 0,
                 display_id: int = 0,
                 agent_callback_id: str = "",
                 init_callback: str = "",
                 last_checkin: str = "",
                 user: str = "",
                 host: str = "",
                 pid: int = 0,
                 ip: str = "",
                 ips: list[str] = [],
                 external_ip: str = "",
                 process_name: str = "",
                 description: str = "",
                 operator_id: int = 0,
                 active: bool = False,
                 integrity_level: int = 0,
                 locked: bool = False,
                 operation_id: int = 0,
                 crypto_type: str = "",
                 os: str = "",
                 architecture: str = "",
                 domain: str = "",
                 extra_info: str = "",
                 sleep_info: str = "",
                 dec_key: str = None,
                 enc_key: str = None,
                 registered_payload_id: int = 0,
                 locked_operator_id: int = 0,
                 timestamp: str = "",
                 **kwargs):
        self.ID = id
        self.DisplayID = display_id
        self.AgentCallbackID = agent_callback_id
        self.InitCallback = init_callback
        self.LastCheckin = last_checkin
        self.User = user
        self.Host = host
        self.PID = pid
        self.IP = ip
        self.IPs = ips
        self.ExternalIp = external_ip
        self.ProcessName = process_name
        self.Description = description
        self.OperatorID = operator_id
        self.Active = active
        self.IntegrityLevel = integrity_level
        self.Locked = locked
        self.OperationID = operation_id
        self.CryptoType = crypto_type
        self.DecKey = base64.b64decode(dec_key) if dec_key is not None else None
        self.EncKey = base64.b64decode(enc_key) if enc_key is not None else None
        self.OS = os
        self.Architecture = architecture
        self.Domain = domain
        self.ExtraInfo = extra_info
        self.SleepInfo = sleep_info
        self.RegisteredPayloadID = registered_payload_id
        self.LockedOperatorID = locked_operator_id
        self.Timestamp = timestamp
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "display_id": self.DisplayID,
            "agent_callback_id": self.AgentCallbackID,
            "init_callback": self.InitCallback,
            "last_checkin": self.LastCheckin,
            "user": self.User,
            "host": self.Host,
            "pid": self.PID,
            "ip": self.IP,
            "ips": self.IPs,
            "external_ip": self.ExternalIp,
            "process_name": self.ProcessName,
            "description": self.Description,
            "operator_id": self.OperatorID,
            "active": self.Active,
            "integrity_level": self.IntegrityLevel,
            "locked": self.Locked,
            "operation_id": self.OperationID,
            "crypto_type": self.CryptoType,
            "dec_key": self.DecKey,
            "enc_key": self.EncKey,
            "os": self.OS,
            "architecture": self.Architecture,
            "domain": self.Domain,
            "extra_info": self.ExtraInfo,
            "sleep_info": self.SleepInfo,
            "timestamp": self.Timestamp,
            "registered_payload_id": self.RegisteredPayloadID,
            "locked_operator_id": self.LockedOperatorID
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class NewArtifactLoggingData:
    """The base information about a new artifact within Mythic

    Attributes:
        ID (int):
            The unique ID of the artifact within Mythic
        TaskID (int):
            The unique ID of the task responsible for this task within Mythic
        Artifact (bytes):
            The actual artifact message
        BaseArtifact (str):
            The type of artifact (ex: Process Create, API, File Write, etc)
        Timestamp (str):
            When this artifact was created
        Host (str):
            The name of the host where this artifact exists
        OperationID (int):
            The unique ID of the operation for this artifact

    """
    def __init__(self,
                 id: int,
                 task_id: int,
                 timestamp: str,
                 artifact: bytes,
                 base_artifact: str,
                 operation_id: int,
                 host: str,
                 **kwargs):
        self.ID = id
        self.TaskID = task_id
        self.Artifact = base64.b64decode(artifact)
        self.Timestamp = timestamp
        self.BaseArtifact = base_artifact
        self.OperationID = operation_id
        self.Host = host
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "task_id": self.TaskID,
            "artifact": base64.b64encode(self.Artifact).decode(),
            "base_artifact": self.BaseArtifact,
            "operation_id": self.OperationID,
            "host": self.Host
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class NewCredentialLoggingData:
    """The base information about a new credential within Mythic

    Attributes:
        ID (int):
            The unique ID of the artifact within Mythic
        Type (str):
            The type of credential
        TaskID (int):
            The unique task ID that created this credential. If this is None then it was manually created in the UI.
        Account (str):
            The account associated with the credential
        Timestamp (str):
            When this artifact was created
        Realm (str):
            The realm (or domain) of the credential
        Credential (str):
            The actual credential material
        OperatorID (int):
            The unique ID for the operator that created this credential
        Comment (str):
            Any comment associated with the credential
        Deleted (bool):
            If this credential was deleted or not
        OperationID (int):
            The unique ID of the operation for this artifact

    """
    def __init__(self,
                 id: int,
                 task_id: int,
                 timestamp: str,
                 type: str,
                 realm: str,
                 operation_id: int,
                 account: str,
                 credential: str,
                 operator_id: int,
                 comment: str,
                 deleted: bool,
                 **kwargs):
        self.ID = id
        self.TaskID = task_id
        self.Type = type
        self.Timestamp = timestamp
        self.Realm = realm
        self.OperationID = operation_id
        self.Account = account
        self.Credential = credential
        self.OperatorID = operator_id
        self.Comment = comment
        self.Deleted = deleted
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "task_id": self.TaskID,
            "type": self.Type,
            "realm": self.Realm,
            "operation_id": self.OperationID,
            "account": self.Account,
            "credential": self.Credential,
            "operator_id": self.OperatorID,
            "comment": self.Comment,
            "deleted": self.Deleted
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class NewFileLoggingData:
    """The base information about a new file within Mythic

    Attributes:
        ID (int):
            The unique ID of the file
        AgentFileID (str):
            The unique UUID of the file
        TotalChunks (int):
            How many total chunks are needed for the file transfer
        ChunksReceived (int):
            How many chunks have been received so far
        ChunkSize (int):
            How many bytes are being sent in each chunk
        TaskID (int):
            The unique ID of the task that's responsible for the file's creation (if any)
        Complete (bool):
            Marks if the file transfer is complete
        Path (str):
            The file path on the Mythic server where this file exists
        FullRemotePath (str):
            Full remote path of where this file was downloaded from or uploaded to on the remote host
        IsPayload (bool):
            Is this file actually a payload file
        IsScreenshot (bool):
            Is this file actually a screenshot
        IsDownloadFromAgent (bool):
            Is this file downloaded from an agent or uploaded?
        MythicTreeID (int):
            The unique ID of a mythictree (file browser) object associated with this file
        Filename (str):
            The filename of the file
        DeleteAfterFetch (bool):
            Was mythic directed to delete the file as soon as an agent successfully retrieved it?
        OperationID (int):
            The unique ID of the operation for this file
        Timestamp (str):
            The time this file was created
        Deleted (bool):
            Was this file deleted?
        OperatorID (int):
            The unique ID of the operator that created this file
        MD5 (str):
            The MD5 Hash of the file
        SHA1 (str):
            The Sha1 Hash of the file
        Comment (str):
            Any comment attached to the file
    """
    def __init__(self,
                 id: int,
                 agent_file_id: str,
                 total_chunks: int,
                 chunks_received: int,
                 chunk_size: int,
                 task_id: int,
                 complete: bool,
                 path: str,
                 full_remote_path: bytes,
                 host: str,
                 is_payload: bool,
                 is_screenshot: bool,
                 is_download_from_agent: bool,
                 mythictree_id: int,
                 filename: bytes,
                 delete_after_fetch: bool,
                 operation_id: int,
                 timestamp: str,
                 deleted: bool,
                 operator_id: int,
                 md5: str,
                 sha1: str,
                 comment: str,
                 **kwargs):
        self.ID = id
        self.AgentFileID = agent_file_id
        self.TotalChunks = total_chunks
        self.ChunksReceived = chunks_received
        self.ChunkSize = chunk_size
        self.TaskID = task_id
        self.Complete = complete
        self.Path = path
        self.FullRemotePath = base64.b64decode(full_remote_path).decode()
        self.Host = host
        self.IsPayload = is_payload
        self.IsScreenshot = is_screenshot
        self.IsDownloadFromAgent = is_download_from_agent
        self.MythicTreeID = mythictree_id
        self.Filename = base64.b64decode(filename).decode()
        self.DeleteAfterFetch = delete_after_fetch
        self.OperationID = operation_id
        self.Timestamp = timestamp
        self.Deleted = deleted
        self.OperatorID = operator_id
        self.MD5 = md5
        self.SHA1 = sha1
        self.Comment = comment
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "agent_file_id": self.AgentFileID,
            "total_chunks": self.TotalChunks,
            "chunks_received": self.ChunksReceived,
            "chunk_size": self.ChunkSize,
            "task_id": self.TaskID,
            "complete": self.Complete,
            "path": self.Path,
            "full_remote_path": base64.b64encode(self.FullRemotePath).decode(),
            "host": self.Host,
            "is_payload": self.IsPayload,
            "is_screenshot": self.IsScreenshot,
            "is_download_from_agent": self.IsDownloadFromAgent,
            "mythictree_id": self.MythicTreeID,
            "filename": base64.b64encode(self.Filename).decode(),
            "delete_after_fetch": self.DeleteAfterFetch,
            "operation_id": self.OperationID,
            "timestamp": self.Timestamp,
            "deleted": self.Deleted,
            "operator_id": self.OperatorID,
            "md5": self.MD5,
            "sha1": self.SHA1,
            "comment": self.Comment,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class NewKeylogLoggingData:
    """The base information about a new keylog within Mythic

    Attributes:
        ID (int):
            The unique ID of the keylog within Mythic
        TaskID (int):
            The unique task ID that created this keylog.
        Keystrokes (bytes):
            The actual keystrokes for this keylog entry
        Timestamp (str):
            When this artifact was created
        Window (str):
            The window title for this keylog entry
        User (str):
            The user associated with this keylog entry
        OperationID (int):
            The unique ID of the operation for this artifact

    """
    def __init__(self,
                 id: int,
                 task_id: int,
                 timestamp: str,
                 operation_id: int,
                 keystrokes: bytes,
                 window: str,
                 user: str,
                 **kwargs):
        self.ID = id
        self.TaskID = task_id
        self.Timestamp = timestamp
        self.Keystrokes = keystrokes
        self.OperationID = operation_id
        self.Window = window
        self.User = user
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "task_id": self.TaskID,
            "keystrokes": self.Keystrokes,
            "timestamp": self.Timestamp,
            "window": self.Window,
            "operation_id": self.OperationID,
            "user": self.User,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class NewPayloadLoggingData:
    """The base information about a new payload within Mythic

    Attributes:
        ID (int):
            The unique ID of the payload within Mythic
        UUID (str):
            The unique UUID of the payload within Mythic
        Description (str):
            The description for the payload used to automatically populate associated callback's descriptions
        OperatorID (int):
            The unique ID of the operator that created this payload
        CreationTime (str):
            The time when this payload was created
        PayloadTypeID (int):
            The unique ID of the payload type for this payload
        OperationID (int):
            The unique ID of the operation for this payload
        WrappedPayloadID (int):
            If this payload wraps another payload, that wrapped payload's unique ID is here
        Deleted (bool):
            Is this payload deleted or not
        BuildPhase (str):
            Was this payload successfully built or not
        BuildMessage (str):
            The build message for the payload
        BuildStderr (str):
            The build stderr for the payload
        BuildStdout (str):
            The build stdout for the payload
        CallbackAlert (bool):
            Should there be a webhook issued for a new callback based on this payload
        AutoGenerated (bool):
            Was this payload created automatically as part of tasking?
        OS (str):
            What was the OS selected as the initial step of building the payload
        TaskID (int):
            If this payload was automatically generated, what was the task ID associated
        FileID (int):
            The unique file ID for this payload
        Timestamp (str):
            The timestamp for the last thing to happen to this payload


    """
    def __init__(self,
                 id: int,
                 uuid: str,
                 description: str,
                 operator_id: int,
                 creation_time: str,
                 payload_type_id: int,
                 operation_id: int,
                 wrapped_payload_id: int,
                 deleted: bool,
                 build_phase: str,
                 build_container: str,
                 build_message: str,
                 build_stderr: str,
                 build_stdout: str,
                 callback_alert: bool,
                 auto_generated: bool,
                 os: str,
                 task_id: int,
                 file_id: int,
                 timestamp: str,
                 **kwargs):
        self.ID = id
        self.UUID = uuid
        self.Description = description
        self.OperatorID = operator_id
        self.CreationTime = creation_time
        self.PayloadTypeID = payload_type_id
        self.Timestamp = timestamp
        self.OperationID = operation_id
        self.WrappedPayloadID = wrapped_payload_id
        self.Deleted = deleted
        self.BuildPhase = build_phase
        self.BuildMessage = build_message
        self.BuildStderr = build_stderr
        self.BuildStdout = build_stdout
        self.CallbackAlert = callback_alert
        self.AutoGenerated = auto_generated
        self.BuildContainer = build_container
        self.OS = os
        self.TaskID = task_id
        self.FileID = file_id
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "uuid": self.UUID,
            "description": self.Description,
            "creation_time": self.CreationTime,
            "payload_type_id": self.PayloadTypeID,
            "wrapped_payload_id": self.WrappedPayloadID,
            "build_container": self.BuildContainer,
            "task_id": self.TaskID,
            "timestamp": self.Timestamp,
            "operation_id": self.OperationID,
            "deleted": self.Deleted,
            "build_phase": self.BuildPhase,
            "build_message": self.BuildMessage,
            "build_stderr": self.BuildStderr,
            "build_stdout": self.BuildStdout,
            "callback_alert": self.CallbackAlert,
            "auto_generated": self.AutoGenerated,
            "os": self.OS,
            "file_id": self.FileID
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class LoggingMessage:
    """The base information about a new logging event

    Attributes:
        OperationID (int): The identifier for the operation
        OperationName (str): The name for the operation
        OperatorUsername (str): The name of the operator that caused this event
        Timestamp (str): The timestamp for this event
        Action (str): What kind of event this is
        Data (any): A subclass that's action dependent with more fields and data

    """
    Data: Union[dict |
                NewCallbackLoggingData |
                NewFileLoggingData |
                NewKeylogLoggingData |
                NewArtifactLoggingData |
                NewCredentialLoggingData |
                NewPayloadLoggingData |
                PTTaskMessageTaskData |
                None]

    def __init__(self,
                 operation_id: int = None,
                 operation_name: str = None,
                 username: str = None,
                 timestamp: str = None,
                 action: str = None,
                 data: dict = None,
                 **kwargs):
        self.OperationID = operation_id
        self.OperationName = operation_name
        self.OperatorUsername = username
        self.Timestamp = timestamp
        self.Action = action
        if self.Action == mythic_container.LOG_TYPE_CALLBACK:
            self.Data = NewCallbackLoggingData(**data)
        elif self.Action == mythic_container.LOG_TYPE_FILE:
            self.Data = NewFileLoggingData(**data)
        elif self.Action == mythic_container.LOG_TYPE_KEYLOG:
            self.Data = NewKeylogLoggingData(**data)
        elif self.Action == mythic_container.LOG_TYPE_ARTIFACT:
            self.Data = NewArtifactLoggingData(**data)
        elif self.Action == mythic_container.LOG_TYPE_CREDENTIAL:
            self.Data = NewCredentialLoggingData(**data)
        elif self.Action == mythic_container.LOG_TYPE_PAYLOAD:
            self.Data = NewPayloadLoggingData(**data)
        elif self.Action == mythic_container.LOG_TYPE_TASK:
            self.Data = PTTaskMessageTaskData(**data)
        else:
            self.Data = data
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "operation_id": self.OperationID,
            "operation_name": self.OperationName,
            "operator_username": self.OperatorUsername,
            "timestamp": self.Timestamp,
            "action": self.Action,
            "data": self.Data.to_json()
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class Log:
    """Log definition class for subscribing to log messages from Mythic


    Attributes:
        LogToFilePath:
            If you want to log to a file, provide the path to that file here
        LogLevel:
            The level you want to log to
        LogMaxSizeInMB:
            The maximum number of MB you want in a single log file before overwriting or rotating
        LogMaxBackups:
            The maximum number of log files before you start overwriting

    Functions:
        new_callback(self, LoggingMessage):
            Handle new callback log messages
        new_credential(self, LoggingMessage):
            Handle new credential log messages
        new_keylog(self, LoggingMessage):
            Handle new keylog log messages
        new_file(self, LoggingMessage):
            Handle new file log messages
        new_payload(self, LoggingMessage):
            Handle new payload log messages
        new_artifact(self, LoggingMessage):
            Handle new artifact log messages
        new_task(self, LoggingMessage):
            Handle new task log messages
    """
    LogToFilePath: str
    LogLevel: str
    LogMaxSizeInMB: int
    LogMaxBackups: int
    new_callback: Callable[[LoggingMessage], Awaitable[None]] = None
    new_credential: Callable[[LoggingMessage], Awaitable[None]] = None
    new_keylog: Callable[[LoggingMessage], Awaitable[None]] = None
    new_file: Callable[[LoggingMessage], Awaitable[None]] = None
    new_payload: Callable[[LoggingMessage], Awaitable[None]] = None
    new_artifact: Callable[[LoggingMessage], Awaitable[None]] = None
    new_task: Callable[[LoggingMessage], Awaitable[None]] = None
