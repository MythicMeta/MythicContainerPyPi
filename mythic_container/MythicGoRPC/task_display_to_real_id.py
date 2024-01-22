import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_TASK_DISPLAY_TO_REAL_ID_SEARCH = "mythic_rpc_task_display_to_real_id_search"


class MythicRPCTaskDisplayToRealIdSearchMessage:
    def __init__(self,
                 TaskDisplayID: int,
                 OperationName: str = "",
                 OperationID: int = None,
                 **kwargs):
        self.TaskDisplayID = TaskDisplayID
        self.OperationName = OperationName
        self.OperationID = OperationID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_display_id": self.TaskDisplayID,
            "operation_name": self.OperationName,
            "operation_id": self.OperationID,
        }

class MythicRPCTaskDisplayToRealIdSearchMessageResponse:

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 task_id: int = 0,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.TaskID = task_id
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCTaskDisplayToRealIdSearch(
        msg: MythicRPCTaskDisplayToRealIdSearchMessage) -> MythicRPCTaskDisplayToRealIdSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TASK_DISPLAY_TO_REAL_ID_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCTaskDisplayToRealIdSearchMessageResponse(**response)
