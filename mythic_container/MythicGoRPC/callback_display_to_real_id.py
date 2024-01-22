import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_CALLBACK_DISPLAY_TO_REAL_ID_SEARCH = "mythic_rpc_callback_display_to_real_id_search"


class MythicRPCCallbackDisplayToRealIdSearchMessage:
    def __init__(self,
                 CallbackDisplayID: int,
                 OperationName: str = "",
                 OperationID: int = None,
                 **kwargs):
        self.CallbackDisplayID = CallbackDisplayID
        self.OperationName = OperationName
        self.OperationID = OperationID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "callback_display_id": self.CallbackDisplayID,
            "operation_name": self.OperationName,
            "operation_id": self.OperationID,
        }

class MythicRPCCallbackDisplayToRealIdSearchMessageResponse:

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 callback_id: int = 0,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.CallbackID = callback_id
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackDisplayToRealIdSearch(
        msg: MythicRPCCallbackDisplayToRealIdSearchMessage) -> MythicRPCCallbackDisplayToRealIdSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_DISPLAY_TO_REAL_ID_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCCallbackDisplayToRealIdSearchMessageResponse(**response)
