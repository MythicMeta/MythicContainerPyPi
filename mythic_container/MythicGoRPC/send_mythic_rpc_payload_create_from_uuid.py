import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_PAYLOAD_CREATE_FROM_UUID = "mythic_rpc_payload_create_from_uuid"


class MythicRPCPayloadCreateFromUUIDMessage:
    def __init__(self,
                 TaskID: int,
                 PayloadUUID: str,
                 NewDescription: str = None,
                 NewFilename: str = None,
                 RemoteHost: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.PayloadUUID = PayloadUUID
        self.NewDescription = NewDescription
        self.NewFilename = NewFilename
        self.RemoteHost = RemoteHost
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "uuid": self.PayloadUUID,
            "new_description": self.NewDescription,
            "new_filename": self.NewFilename,
            "remote_host": self.RemoteHost
        }


class MythicRPCPayloadCreateFromUUIDMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 new_payload_uuid: str = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.NewPayloadUUID = new_payload_uuid
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCPayloadCreateFromUUID(
        msg: MythicRPCPayloadCreateFromUUIDMessage) -> MythicRPCPayloadCreateFromUUIDMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_PAYLOAD_CREATE_FROM_UUID,
                                                                            body=msg.to_json())
    return MythicRPCPayloadCreateFromUUIDMessageResponse(**response)
