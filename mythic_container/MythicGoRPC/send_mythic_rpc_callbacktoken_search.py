import mythic_container
from mythic_container.logging import logger
import time

MYTHIC_RPC_CALLBACKTOKEN_SEARCH = "mythic_rpc_callbacktoken_search"

class MythicRPCCallbackTokenSearchToken:
    def __init__(self,
                 id: int = None,
                 task_id: int = None,
                 deleted: bool = None,
                 host: str = None,
                 description: str = None,
                 operation_id: int = None,
                 timestamp: str = None,
                 token_id: int = None,
                 user: str = None,
                 groups: str = None,
                 privileges: str = None,
                 thread_id: int = None,
                 process_id: int = None,
                 session_id: int = None,
                 logon_sid: str = None,
                 integrity_level_sid: str = None,
                 app_container_sid: str = None,
                 app_container_number: int = None,
                 default_dacl: str = None,
                 restricted: bool = None,
                 handle: int = None,
                 capabilities: str = None,
                 **kwargs):
        self.ID = id
        self.TaskID = task_id
        self.Deleted = deleted
        self.Host = host
        self.Description = description
        self.OperationID = operation_id
        self.Timestamp = timestamp
        self.TokenID = token_id
        self.User = user
        self.Groups = groups
        self.Privileges = privileges
        self.ThreadID = thread_id
        self.ProcessID = process_id
        self.SessionID = session_id
        self.LogonSID = logon_sid
        self.IntegrityLevelSID = integrity_level_sid
        self.AppContainerSID = app_container_sid
        self.AppContainerNumber = app_container_number
        self.DefaultDACL = default_dacl
        self.Restricted = restricted
        self.Handle = handle
        self.Capabilities = capabilities
    def to_json(self):
        return {
            "id": self.ID,
            "task_id": self.TaskID,
            "deleted": self.Deleted,
            "host": self.Host,
            "description": self.Description,
            "operation_id": self.OperationID,
            "timestamp": self.Timestamp,
            "token_id": self.TokenID,
            "user": self.User,
            "groups": self.Groups,
            "privileges": self.Privileges,
            "thread_id": self.ThreadID,
            "process_id": self.ProcessID,
            "session_id": self.SessionID,
            "logon_sid": self.LogonSID,
            "integrity_level_sid": self.IntegrityLevelSID,
            "app_container_sid": self.AppContainerSID,
            "app_container_number": self.AppContainerNumber,
            "default_dacl": self.DefaultDACL,
            "restricted": self.Restricted,
            "handle": self.Handle,
            "capabilities": self.Capabilities,
        }
class MythicRPCCallbackSearchTokenData:
    Token: MythicRPCCallbackTokenSearchToken
    def __init__(self,
                 id: int = None,
                 token: dict = None,
                 callback_id: int = None,
                 task_id: int = None,
                 timestamp_created: str = None,
                 deleted: bool = None,
                 host: str = None,
                 **kwargs):
        self.ID = id
        self.Token = MythicRPCCallbackTokenSearchToken(**token)
        self.CallbackID = callback_id
        self.TaskID = task_id
        self.TimestampCreated = timestamp_created
        self.Deleted = deleted
        self.Host = host
    def to_json(self):
        return {
            "id": self.ID,
            "token": self.Token.to_json() if self.Token else None,
            "callback_id": self.CallbackID,
            "task_id": self.TaskID,
            "timestamp_created": self.TimestampCreated,
            "deleted": self.Deleted,
            "host": self.Host
        }



class MythicRPCCallbackTokenSearchMessage:
    def __init__(self,
                 TaskID: int = None,
                 CallbackID: int = None,
                 AgentCallbackID: str = None):
        self.TaskID = TaskID
        self.CallbackID = CallbackID
        self.AgentCallbackID = AgentCallbackID
    def to_json(self):
        return {
            "task_id": self.TaskID,
            "callback_id": self.CallbackID,
            "agent_callback_id": self.AgentCallbackID
        }


class MythicRPCCallbackTokenSearchMessageResponse:
    def __init__(self,
                 success: bool = None,
                 error: str = None,
                 callbacktokens: list[dict] = None):
        self.Success = success
        self.Error = error
        self.CallbackTokens = [MythicRPCCallbackSearchTokenData(**x) for x in callbacktokens] if callbacktokens else []



async def SendMythicRPCCallbackTokenSearch(
        msg: MythicRPCCallbackTokenSearchMessage) -> MythicRPCCallbackTokenSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACKTOKEN_SEARCH,
                                                                            body=msg.to_json())
    finalResponse = MythicRPCCallbackTokenSearchMessageResponse(**response)
    return finalResponse
