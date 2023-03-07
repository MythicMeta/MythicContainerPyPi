import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_PAYLOAD_ADD_COMMAND = "mythic_rpc_payload_add_command"


class MythicRPCPayloadAddCommandMessage:
    def __init__(self,
                 PayloadUUID: str,
                 Commands: list[str],
                 **kwargs):
        self.PayloadUUID = PayloadUUID
        self.Commands = Commands
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "payload_uuid": self.PayloadUUID,
            "commands": self.Commands
        }


class MythicRPCPayloadAddCommandMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCPayloadAddCommand(
        msg: MythicRPCPayloadAddCommandMessage) -> MythicRPCPayloadAddCommandMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_PAYLOAD_ADD_COMMAND,
                                                                            body=msg.to_json())
    return MythicRPCPayloadAddCommandMessageResponse(**response)
