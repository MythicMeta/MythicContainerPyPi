import mythic_container
from mythic_container.logging import logger
from mythic_container.utils_mythic_file_transfer import getFileFromMythic

MYTHIC_RPC_FILE_GET_CONTENT = "mythic_rpc_file_get_content"


class MythicRPCFileGetContentMessage:
    def __init__(self,
                 AgentFileId: str,
                 **kwargs):
        self.AgentFileId = AgentFileId
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "file_id": self.AgentFileId,
        }


class MythicRPCFileGetContentMessageResponse:
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


async def SendMythicRPCFileGetContent(
        msg: MythicRPCFileGetContentMessage) -> MythicRPCFileGetContentMessageResponse:
    content = await getFileFromMythic(agentFileId=msg.AgentFileId)

    return MythicRPCFileGetContentMessageResponse(
        success=content is not None,
        error="Failed to fetch file from Mythic" if content is None else "",
        content=content
    )
