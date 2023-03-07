import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_TASK_UPDATE = "mythic_rpc_task_update"


class MythicRPCTaskUpdateMessage:
    def __init__(self,
                 TaskID: int,
                 UpdateStatus: str = None,
                 UpdateStdout: str = None,
                 UpdateStderr: str = None,
                 UpdateCommandName: str = None,
                 UpdateCompleted: bool = None,
                 **kwargs):
        self.TaskID = TaskID
        self.UpdateStatus = UpdateStatus
        self.UpdateStdout = UpdateStdout
        self.UpdateStderr = UpdateStderr
        self.UpdateCommandName = UpdateCommandName
        self.UpdateCompleted = UpdateCompleted
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "update_status": self.UpdateStatus,
            "update_stdout": self.UpdateStdout,
            "update_stderr": self.UpdateStderr,
            "update_command_name": self.UpdateCommandName,
            "update_completed": self.UpdateCompleted
        }


class MythicRPCTaskUpdateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCTaskUpdate(
        msg: MythicRPCTaskUpdateMessage) -> MythicRPCTaskUpdateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TASK_UPDATE,
                                                                            body=msg.to_json())
    return MythicRPCTaskUpdateMessageResponse(**response)
