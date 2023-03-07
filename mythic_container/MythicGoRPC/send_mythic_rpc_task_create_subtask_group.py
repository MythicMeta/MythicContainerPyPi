import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_TASK_CREATE_SUBTASK_GROUP = "mythic_rpc_task_create_group"


class MythicRPCTaskCreateSubtaskGroupTasks:
    def __init__(self,
                 SubtaskCallbackFunction: str = None,
                 CommandName: str = None,
                 Params: str = None,
                 ParameterGroupName: str = None,
                 Token: int = None,
                 **kwargs):
        self.SubtaskCallbackFunction = SubtaskCallbackFunction
        self.CommandName = CommandName
        self.Params = Params
        self.ParameterGroupName = ParameterGroupName
        self.Token = Token
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return {
            "subtask_callback_function": self.SubtaskCallbackFunction,
            "command_name": self.CommandName,
            "params": self.Params,
            "parameter_group_name": self.ParameterGroupName,
            "token": self.Token
        }

class MythicRPCTaskCreateSubtaskGroupMessage:
    def __init__(self,
                 TaskID: int,
                 GroupName: str,
                 GroupCallbackFunction: str = None,
                 Tasks: list[MythicRPCTaskCreateSubtaskGroupTasks] = None,
                 **kwargs):
        self.TaskID = TaskID
        self.GroupName = GroupName
        self.GroupCallbackFunction = GroupCallbackFunction
        self.Tasks = Tasks
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "group_name": self.GroupName,
            "group_callback_function": self.GroupCallbackFunction,
            "tasks": [x.to_json() for x in self.Tasks]
        }


class MythicRPCTaskCreateSubtaskGroupMessageResponse:
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


async def SendMythicRPCTaskCreateSubtaskGroup(
        msg: MythicRPCTaskCreateSubtaskGroupMessage) -> MythicRPCTaskCreateSubtaskGroupMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TASK_CREATE_SUBTASK_GROUP,
                                                                            body=msg.to_json())
    return MythicRPCTaskCreateSubtaskGroupMessageResponse(**response)
