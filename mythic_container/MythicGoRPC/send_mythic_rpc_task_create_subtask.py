import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_TASK_CREATE_SUBTASK = "mythic_rpc_task_create_subtask"


class MythicRPCTaskCreateSubtaskMessage:
    def __init__(self,
                 TaskID: int,
                 SubtaskCallbackFunction: str = None,
                 CommandName: str = None,
                 Params: str = None,
                 ParameterGroupName: str = None,
                 Token: int = None,
                 **kwargs):
        self.TaskID = TaskID
        self.SubtaskCallbackFunction = SubtaskCallbackFunction
        self.CommandName = CommandName
        self.Params = Params
        self.ParameterGroupName = ParameterGroupName
        self.Token = Token
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "subtask_callback_function": self.SubtaskCallbackFunction,
            "command_name": self.CommandName,
            "params": self.Params,
            "parameter_group_name": self.ParameterGroupName,
            "token": self.Token
        }


class MythicRPCTaskCreateSubtaskMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 task_id: int = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.TaskID = task_id
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCTaskCreateSubtask(
        msg: MythicRPCTaskCreateSubtaskMessage) -> MythicRPCTaskCreateSubtaskMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TASK_CREATE_SUBTASK,
                                                                            body=msg.to_json())
    return MythicRPCTaskCreateSubtaskMessageResponse(**response)
