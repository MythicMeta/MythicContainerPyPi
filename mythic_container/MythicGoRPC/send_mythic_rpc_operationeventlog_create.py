import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_EVENTLOG_CREATE = "mythic_rpc_eventlog_create"


class MythicRPCOperationEventLogCreateMessage:
    def __init__(self,
                 TaskID: int = None,
                 CallbackId: int = None,
                 CallbackAgentId: str = None,
                 OperationId: int = None,
                 Message: str = None,
                 MessageLevel: str = "info",  # only info or warning available for now
                 **kwargs):
        self.TaskID = TaskID
        self.CallbackId = CallbackId
        self.CallbackAgentId = CallbackAgentId
        self.OperationId = OperationId
        self.Message = Message
        self.MessageLevel = MessageLevel
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "callback_id": self.CallbackId,
            "callback_agent_id": self.CallbackAgentId,
            "operation_id": self.OperationId,
            "message": self.Message,
            "level": self.MessageLevel
        }


class MythicRPCOperationEventLogCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCOperationEventLogCreate(
        msg: MythicRPCOperationEventLogCreateMessage) -> MythicRPCOperationEventLogCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_EVENTLOG_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCOperationEventLogCreateMessageResponse(*response)
