import mythic_container
from mythic_container.logging import logger
from .send_mythic_rpc_callbacktoken_create import MythicRPCCallbackTokenData

MYTHIC_RPC_CALLBACKTOKEN_REMOVE = "mythic_rpc_callbacktoken_remove"

class MythicRPCCallbackTokenRemoveMessage:
    def __init__(self,
                 TaskID: int,
                 CallbackTokens: list[MythicRPCCallbackTokenData],
                 **kwargs):
        self.TaskID = TaskID
        self.CallbackTokens = CallbackTokens
        for k, v in kwargs.items():
            logger.debug("Unknown kwarg %s: %s", k, v)

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "callbacktokens": [x.to_json() for x in self.CallbackTokens]
        }


class MythicRPCCallbackTokenRemoveMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.debug("Unknown kwarg %s: %s", k, v)


async def SendMythicRPCCallbackTokenRemove(
        msg: MythicRPCCallbackTokenRemoveMessage) -> MythicRPCCallbackTokenRemoveMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACKTOKEN_REMOVE,
                                                                            body=msg.to_json())
    return MythicRPCCallbackTokenRemoveMessageResponse(**response)
