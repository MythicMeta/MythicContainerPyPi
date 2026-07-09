import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_CHAT_CHANNEL_METADATA_UPDATE = "mythic_rpc_chat_channel_metadata_update"


class MythicRPCChatChannelMetadataUpdateMessage:
    def __init__(
            self,
            OperationID: int = 0,
            ChannelID: int = 0,
            ContainerName: str = "",
            ChannelMetadata: dict = None,
            **kwargs):
        self.OperationID = OperationID
        self.ChannelID = ChannelID
        self.ContainerName = ContainerName
        self.ChannelMetadata = ChannelMetadata if ChannelMetadata is not None else {}
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "operation_id": self.OperationID,
            "channel_id": self.ChannelID,
            "container_name": self.ContainerName,
            "channel_metadata": self.ChannelMetadata,
        }


class MythicRPCChatChannelMetadataUpdateMessageResponse:
    def __init__(
            self,
            success: bool = False,
            error: str = "",
            **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCChatChannelMetadataUpdate(
        msg: MythicRPCChatChannelMetadataUpdateMessage) -> MythicRPCChatChannelMetadataUpdateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
        queue=MYTHIC_RPC_CHAT_CHANNEL_METADATA_UPDATE,
        body=msg.to_json(),
    )
    return MythicRPCChatChannelMetadataUpdateMessageResponse(**response)
