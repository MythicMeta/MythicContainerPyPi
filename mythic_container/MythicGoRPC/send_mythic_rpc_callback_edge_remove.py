import mythic_container
from mythic_container.logging import logger
from mythic_container.MythicGoRPC.send_mythic_rpc_callback_search import MythicRPCCallbackSearchMessageResult
import time

MYTHIC_RPC_CALLBACK_EDGE_REMOVE = "mythic_rpc_callback_edge_remove"


class MythicRPCCallbackEdgeRemoveMessage:
    def __init__(self,
                 SourceCallbackID: int,
                 DestinationCallbackID: int,
                 C2ProfileName: str,
                 **kwargs):
        self.SourceCallbackID = SourceCallbackID
        self.DestinationCallbackID = DestinationCallbackID
        self.C2ProfileName = C2ProfileName
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "source_callback_id": self.SourceCallbackID,
            "destination_callback_id": self.DestinationCallbackID,
            "c2_profile_name": self.C2ProfileName,
        }

class MythicRPCCallbackEdgeRemoveMessageResponse:

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackEdgeRemove(
        msg: MythicRPCCallbackEdgeRemoveMessage) -> MythicRPCCallbackEdgeRemoveMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_EDGE_REMOVE,
                                                                            body=msg.to_json())
    return MythicRPCCallbackEdgeRemoveMessageResponse(**response)
