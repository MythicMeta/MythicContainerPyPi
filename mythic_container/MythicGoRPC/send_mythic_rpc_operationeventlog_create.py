import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_EVENTLOG_CREATE = "mythic_rpc_eventlog_create"

MESSAGE_LEVEL_INFO           = "info"
MESSAGE_LEVEL_DEBUG          = "debug"
MESSAGE_LEVEL_AUTH           = "auth"
MESSAGE_LEVEL_AGENT_MESSAGE  = "agent"
MESSAGE_LEVEL_API            = "api"

class MythicRPCOperationEventLogCreateMessage:
    def __init__(self,
                 TaskID: int = None,
                 CallbackID: int = None,
                 AgentCallbackID: str = None,
                 OperationID: int = None,
                 Message: str = None,
                 MessageLevel: str = "info",  # info, debug, auth, api, agent_message
                 Warning: bool = False,
                 **kwargs):
        self.TaskID = TaskID
        self.CallbackID = CallbackID
        self.AgentCallbackID = AgentCallbackID
        self.OperationID = OperationID
        self.Message = Message
        self.MessageLevel = MessageLevel
        self.Warning = Warning
        for k, v in kwargs.items():
            if k == "CallbackId":
                self.CallbackID = v
                logger.warning("MythicRPCOperationEventLogCreateMessage using old API call, update CallbackId to CallbackID")
                continue
            if k == "AgentCallbackId":
                self.AgentCallbackID = v
                logger.warning("MythicRPCOperationEventLogCreateMessage using old API call, update AgentCallbackId to AgentCallbackID")
                continue
            if k == "OperationId":
                self.OperationID = v
                logger.warning("MythicRPCOperationEventLogCreateMessage using old API call, update OperationId to OperationID")
                continue
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "callback_id": self.CallbackID,
            "callback_agent_id": self.AgentCallbackID,
            "operation_id": self.OperationID,
            "message": self.Message,
            "level": self.MessageLevel,
            "warning": self.Warning
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
