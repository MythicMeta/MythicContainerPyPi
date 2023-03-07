import mythic_container
from mythic_container.logging import logger
import base64

MYTHIC_RPC_CALLBACK_DECRYPT_BYTES = "mythic_rpc_callback_decrypt_bytes"


class MythicRPCCallbackDecryptBytesMessage:
    def __init__(self,
                 AgentCallbackUUID: str,
                 Message: bytes,
                 IncludesUUID: bool = False,
                 IsBase64Encoded: bool = True,
                 **kwargs):
        self.AgentCallbackUUID = AgentCallbackUUID
        self.Message = Message
        self.IncludesUUID = IncludesUUID
        self.IsBase64Encoded = IsBase64Encoded
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "agent_callback_id": self.AgentCallbackUUID,
            "message": base64.b64encode(self.Message).decode(),
            "include_uuid": self.IncludesUUID,
            "base64_message": self.IsBase64Encoded
        }


class MythicRPCCallbackDecryptBytesMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 message: bytes = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Message = message
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackDecryptBytes(
        msg: MythicRPCCallbackDecryptBytesMessage) -> MythicRPCCallbackDecryptBytesMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_DECRYPT_BYTES,
                                                                            body=msg.to_json())
    return MythicRPCCallbackDecryptBytesMessageResponse(**response)
