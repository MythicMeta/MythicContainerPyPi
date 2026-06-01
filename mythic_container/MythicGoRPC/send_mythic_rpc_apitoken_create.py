import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_APITOKEN_CREATE = "mythic_rpc_apitoken_create"


class MythicRPCAPITokenCreateMessage:
    def __init__(self,
                 AgentTaskID: str = None,
                 AgentCallbackID: str = None,
                 PayloadUUID: str = None,
                 ChatChannelID: int = None,
                 APITokenID: int = None,
                 Scopes: list[str] = None,
                 OperationID: int = None,
                 **kwargs):
        self.AgentTaskID = AgentTaskID
        self.AgentCallbackID = AgentCallbackID
        self.PayloadUUID = PayloadUUID
        self.ChatChannelID = ChatChannelID
        self.APITokenID = APITokenID
        self.Scopes = Scopes if Scopes is not None else []
        self.OperationID = OperationID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "agent_task_id": self.AgentTaskID,
            "agent_callback_id": self.AgentCallbackID,
            "payload_uuid": self.PayloadUUID,
            "chat_channel_id": self.ChatChannelID,
            "apitoken_id": self.APITokenID,
            "scopes": self.Scopes,
            "operation_id": self.OperationID,
        }


class MythicRPCAPITokenCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 apitoken: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        self.APIToken = apitoken
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCAPITokenCreate(
        msg: MythicRPCAPITokenCreateMessage) -> MythicRPCAPITokenCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_APITOKEN_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCAPITokenCreateMessageResponse(**response)
