import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_TASK_CREATE = "mythic_rpc_task_create"


class MythicRPCTaskCreateMessage:
    """
    Needs OperatorID, TaskID, or EventStepInstanceID to associate this task with the appropriate user
    """
    def __init__(self,
                 AgentCallbackID: str = None,
                 CallbackID: int = None,
                 OperatorID: int = None,
                 TaskID: int = None,
                 EventStepInstanceID: int = None,
                 CommandName: str = None,
                 Params: str = None,
                 ParameterGroupName: str = None,
                 Token: int = None,
                 **kwargs):
        self.AgentCallbackID = AgentCallbackID
        self.CallbackID = CallbackID
        self.CommandName = CommandName
        self.Params = Params
        self.ParameterGroupName = ParameterGroupName
        self.Token = Token
        self.OperatorID = OperatorID
        self.TaskID = TaskID
        self.EventStepInstanceID = EventStepInstanceID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "agent_callback_id": self.AgentCallbackID,
            "callback_id": self.CallbackID,
            "command_name": self.CommandName,
            "params": self.Params,
            "parameter_group_name": self.ParameterGroupName,
            "token": self.Token,
            "eventstepinstance_id": self.EventStepInstanceID,
            "operator_id": self.OperatorID,
            "task_id": self.TaskID,
        }


class MythicRPCTaskCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 task_id: int = None,
                 task_display_id: int = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.TaskID = task_id
        self.TaskDisplayID = task_display_id
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "task_id": self.TaskID,
            "task_display_id": self.TaskDisplayID,
        }


async def SendMythicRPCTaskCreate(
        msg: MythicRPCTaskCreateMessage) -> MythicRPCTaskCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TASK_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCTaskCreateMessageResponse(**response)
