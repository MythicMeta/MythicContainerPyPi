import mythic_container
from mythic_container.logging import logger
import base64

MYTHIC_RPC_AGENTSTORAGE_CREATE = "mythic_rpc_agentstorage_create"


class MythicRPCAgentstorageCreateMessage:
    def __init__(self,
                 UniqueID: str,
                 DataToStore: bytes,
                 **kwargs):
        self.UniqueID = UniqueID
        self.DataToStore = DataToStore
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "unique_id": self.UniqueID,
            "data": base64.b64encode(self.DataToStore).decode()
        }


class MythicRPCAgentstorageCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCAgentStorageCreate(
        msg: MythicRPCAgentstorageCreateMessage) -> MythicRPCAgentstorageCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_AGENTSTORAGE_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCAgentstorageCreateMessageResponse(**response)
