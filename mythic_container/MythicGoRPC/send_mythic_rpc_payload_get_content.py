import mythic_container
from mythic_container.logging import logger
from mythic_container.utils_mythic_file_transfer import getFileFromMythic

MYTHIC_RPC_PAYLOAD_GET_PAYLOAD_CONTENT = "mythic_rpc_payload_get_content"


class MythicRPCPayloadGetContentMessage:
    def __init__(self,
                 PayloadUUID: str,
                 **kwargs):
        self.PayloadUUID = PayloadUUID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "uuid": self.PayloadUUID,
        }


class MythicRPCPayloadGetContentMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 content: bytes = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Content = content
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCPayloadGetContent(
        msg: MythicRPCPayloadGetContentMessage) -> MythicRPCPayloadGetContentMessageResponse:
    content = await getFileFromMythic(agentFileId=msg.PayloadUUID)

    return MythicRPCPayloadGetContentMessageResponse(
        success=content is not None,
        error="Failed to fetch file from Mythic" if content is None else "",
        content=content
    )
