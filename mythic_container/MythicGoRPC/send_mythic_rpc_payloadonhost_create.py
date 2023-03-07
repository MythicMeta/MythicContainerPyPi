import mythic_container
from mythic_container.logging import logger
from mythic_container.utils_mythic_file_transfer import getFileFromMythic

MYTHIC_RPC_PAYLOADONHOST_CREATE = "mythic_rpc_payloadonhost_create"


class MythicRPCPayloadOnHostCreateData:
    def __init__(self,
                 Host: str = None,
                 PayloadId: int = None,
                 PayloadUUID: str = None,
                 **kwargs):
        self.Host = Host
        self.PayloadId = PayloadId
        self.PayloadUUID = PayloadUUID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return {
            "host": self.Host,
            "payload_id": self.PayloadId,
            "payload_uuid": self.PayloadUUID
        }

class MythicRPCPayloadOnHostCreateMessage:
    def __init__(self,
                 TaskID: int,
                 PayloadOnHost: MythicRPCPayloadOnHostCreateData = None,
                 **kwargs):
        self.TaskID = TaskID
        self.PayloadOnHost = PayloadOnHost
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "payload_on_host": self.PayloadOnHost
        }


class MythicRPCPayloadOnHostCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCPayloadOnHostCreate(
        msg: MythicRPCPayloadOnHostCreateMessage) -> MythicRPCPayloadOnHostCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_PAYLOADONHOST_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCPayloadOnHostCreateMessageResponse(**response)
