import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_CALLBACKTOKEN_CREATE = "mythic_rpc_callbacktoken_create"

class Token:
    def __init__(self,
                 Action: str = None, # for token_create not callbacktoken_create
                 TokenID: int = None, # for token_create not callbacktoken_create
                 User: str = None,
                 Groups: str = None,
                 Privileges: str = None,
                 ThreadID: int = None,
                 ProcessID: int = None,
                 SessionID: int = None,
                 LogonSID: str = None,
                 IntegrityLevelSID: str = None,
                 Restricted: bool = None,
                 DefaultDacl: str = None,
                 Handle: int = None,
                 Capabilities: str = None,
                 AppContainerSID: str = None,
                 AppContainerNumber: int = None,
                 **kwargs):
        self.Action = Action
        self.TokenID = TokenID
        self.User = User
        self.Groups = Groups
        self.Privileges = Privileges
        self.ThreadID = ThreadID
        self.ProcessID = ProcessID
        self.SessionID = SessionID
        self.LogonSID = LogonSID
        self.IntegrityLevelSID = IntegrityLevelSID
        self.Restricted = Restricted
        self.DefaultDacl = DefaultDacl
        self.Handle = Handle
        self.Capabilities = Capabilities
        self.AppContainerSID = AppContainerSID
        self.AppContainerNumber = AppContainerNumber
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return {
            "action": self.Action,
            "token_id": self.TokenID,
            "user": self.User,
            "groups": self.Groups,
            "privileges": self.Privileges,
            "thread_id": self.ThreadID,
            "process_id": self.ProcessID,
            "session_id": self.SessionID,
            "logon_sid": self.LogonSID,
            "integrity_level_sid": self.IntegrityLevelSID,
            "restricted": self.Restricted,
            "default_dacl": self.DefaultDacl,
            "handle": self.Handle,
            "capabilities": self.Capabilities,
            "app_container_sid": self.AppContainerSID,
            "app_container_number": self.AppContainerNumber
        }
class MythicRPCCallbackTokenData:
    def __init__(self,
                 Action: str = "add",
                 Host: str = None,
                 TokenId: int = None,
                 TokenInfo: Token = None,
                 **kwargs):
        self.Host = Host
        self.Action = Action
        self.TokenInfo = TokenInfo
        self.TokenId = TokenId
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "host": self.Host,
            "action": self.Action,
            "token": self.TokenInfo.to_json() if self.TokenInfo is not None else None,
            "TokenId": self.TokenId
        }


class MythicRPCCallbackTokenCreateMessage:
    def __init__(self,
                 TaskID: int,
                 CallbackTokens: list[MythicRPCCallbackTokenData],
                 **kwargs):
        self.TaskID = TaskID
        self.CallbackTokens = CallbackTokens
        for k, v in kwargs:
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "callbacktokens": [x.to_json() for x in self.CallbackTokens]
        }


class MythicRPCCallbackTokenCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackTokenCreate(
        msg: MythicRPCCallbackTokenCreateMessage) -> MythicRPCCallbackTokenCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACKTOKEN_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCCallbackTokenCreateMessageResponse(**response)
