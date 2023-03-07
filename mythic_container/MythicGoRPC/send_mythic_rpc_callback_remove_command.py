import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_CALLBACK_REMOVE_COMMAND = "mythic_rpc_callback_remove_command"


class MythicRPCCallbackRemoveCommandMessage:
    def __init__(self,
                 TaskID: int,
                 Commands: list[str],
                 **kwargs):
        self.TaskID = TaskID
        self.Commands = Commands
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "commands": self.Commands
        }


class MythicRPCCallbackRemoveCommandMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackRemoveCommand(
        msg: MythicRPCCallbackRemoveCommandMessage) -> MythicRPCCallbackRemoveCommandMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_REMOVE_COMMAND,
                                                                            body=msg.to_json())
    return MythicRPCCallbackRemoveCommandMessageResponse(**response)
