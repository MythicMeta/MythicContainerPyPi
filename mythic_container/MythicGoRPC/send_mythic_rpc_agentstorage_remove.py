import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_AGENTSTORAGE_REMOVE = "mythic_rpc_agentstorage_remove"


class MythicRPCAgentStorageRemoveMessage:
    def __init__(self,
                 UniqueID: str,
                 **kwargs):
        self.UniqueID = UniqueID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "unique_id": self.UniqueID,
        }


class MythicRPCAgentStorageRemoveMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCAgentStorageRemove(
        msg: MythicRPCAgentStorageRemoveMessage) -> MythicRPCAgentStorageRemoveMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_AGENTSTORAGE_REMOVE,
                                                                            body=msg.to_json())
    return MythicRPCAgentStorageRemoveMessageResponse(**response)
