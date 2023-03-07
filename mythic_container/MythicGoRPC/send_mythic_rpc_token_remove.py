import mythic_container
from mythic_container.logging import logger
from .send_mythic_rpc_callbacktoken_create import Token

MYTHIC_RPC_TOKEN_REMOVE = "mythic_rpc_token_remove"



class MythicRPCTokenRemoveMessage:
    def __init__(self,
                 TaskID: int,
                 Tokens: list[Token],
                 **kwargs):
        self.TaskID = TaskID
        self.Tokens = Tokens
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "tokens": [x.to_json() for x in self.Tokens]
        }


class MythicRPCTokenRemoveMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCTokenRemove(
        msg: MythicRPCTokenRemoveMessage) -> MythicRPCTokenRemoveMessageResponse:
    for t in msg.Tokens:
        t.Action = "remove"
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TOKEN_REMOVE,
                                                                            body=msg.to_json())
    return MythicRPCTokenRemoveMessageResponse(**response)
