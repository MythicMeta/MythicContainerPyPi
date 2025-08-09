import mythic_container
from mythic_container.logging import logger
from mythic_container.utils_mythic_file_transfer import sendFileToMythic

MYTHIC_RPC_FILE_CREATE = "mythic_rpc_file_create"


class MythicRPCFileCreateMessage:
    """
    Must supply TaskID, PayloadUUID, or AgentCallbackID in order to properly assign the file to your operation
    """
    def __init__(self,
                 TaskID: int = 0,
                 PayloadUUID: str = "",
                 AgentCallbackID: str = "",
                 FileContents: bytes = None,
                 DeleteAfterFetch: bool = False,
                 Filename: str = None,
                 IsScreenshot: bool = False,
                 IsDownloadFromAgent: bool = False,
                 RemotePathOnTarget: str = "",
                 TargetHostName: str = "",
                 Comment: str = "",
                 **kwargs):
        self.TaskID = TaskID
        self.PayloadUUID = PayloadUUID
        self.AgentCallbackID = AgentCallbackID
        self.FileContents = FileContents
        self.DeleteAfterFetch = DeleteAfterFetch
        self.Filename = Filename
        self.IsScreenshot = IsScreenshot
        self.IsDownloadFromAgent = IsDownloadFromAgent
        self.RemotePathOnTarget = RemotePathOnTarget
        self.TargetHostName = TargetHostName
        self.Comment = Comment
        for k, v in kwargs.items():
            logger.debug("Unknown kwarg %s: %s", k, v)

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "payload_uuid": self.PayloadUUID,
            "agent_callback_id": self.AgentCallbackID,
            "delete_after_fetch": self.DeleteAfterFetch,
            "filename": self.Filename,
            "is_screenshot": self.IsScreenshot,
            "is_download": self.IsDownloadFromAgent,
            "remote_path": self.RemotePathOnTarget,
            "host": self.TargetHostName,
            "comment": self.Comment
        }


class MythicRPCFileCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 agent_file_id: str = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.AgentFileId = agent_file_id
        for k, v in kwargs.items():
            logger.debug("Unknown kwarg %s: %s", k, v)


async def SendMythicRPCFileCreate(
        msg: MythicRPCFileCreateMessage) -> MythicRPCFileCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_FILE_CREATE,
                                                                            body=msg.to_json())
    finalResponse = MythicRPCFileCreateMessageResponse(**response)
    if finalResponse.Success and finalResponse.AgentFileId is not None:
        # we need to ship off the file contents now
        if await sendFileToMythic(msg.FileContents, finalResponse.AgentFileId):
            return finalResponse
        else:
            finalResponse.Success = False
            finalResponse.Error = "Failed to upload file contents to Mythic over HTTP"
            return finalResponse
    return finalResponse
