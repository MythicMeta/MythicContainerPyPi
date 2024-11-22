import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_CALLBACK_ADD_COMMAND = "mythic_rpc_callback_add_command"


class MythicRPCCallbackAddCommandMessage:
    def __init__(self,
                 Commands: list[str],
                 TaskID: int = None,
                 CallbackAgentUUID: str = None,
                 PayloadType: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.CallbackAgentUUID = CallbackAgentUUID
        self.Commands = Commands
        self.PayloadType = PayloadType
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "commands": self.Commands,
            "callback_agent_id": self.CallbackAgentUUID,
            "payload_type": self.PayloadType
        }


class MythicRPCCallbackAddCommandMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackAddCommand(
        msg: MythicRPCCallbackAddCommandMessage) -> MythicRPCCallbackAddCommandMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_ADD_COMMAND,
                                                                            body=msg.to_json())
    return MythicRPCCallbackAddCommandMessageResponse(**response)
