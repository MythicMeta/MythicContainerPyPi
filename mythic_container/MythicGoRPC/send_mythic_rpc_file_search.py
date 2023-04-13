import mythic_container
from mythic_container.logging import logger
import time

MYTHIC_RPC_FILE_SEARCH = "mythic_rpc_file_search"


class MythicRPCFileSearchMessage:
    def __init__(self,
                 TaskID: int = None,
                 CallbackID: int = None,
                 LimitByCallback: bool = False,
                 MaxResults: int = -1,
                 Filename: str = None,
                 IsScreenshot: bool = False,
                 IsDownloadFromAgent: bool = False,
                 IsPayload: bool = False,
                 AgentFileID: str = None,
                 Comment: str = "",
                 **kwargs):
        self.TaskID = TaskID
        self.CallbackID = CallbackID
        self.LimitByCallback = LimitByCallback
        self.MaxResults = MaxResults
        self.Filename = Filename
        self.IsScreenshot = IsScreenshot
        self.IsDownloadFromAgent = IsDownloadFromAgent
        self.Comment = Comment
        self.IsPayload = IsPayload
        self.AgentFileID = AgentFileID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "callback_id": self.CallbackID,
            "limit_by_callback": self.LimitByCallback,
            "max_results": self.MaxResults,
            "filename": self.Filename,
            "is_screenshot": self.IsScreenshot,
            "is_download_from_agent": self.IsDownloadFromAgent,
            "is_payload": self.IsPayload,
            "file_id": self.AgentFileID,
            "comment": self.Comment
        }


class FileData:
    def __init__(self,
                 agent_file_id: str = None,
                 filename: str = None,
                 comment: str = None,
                 is_payload: bool = None,
                 is_download_from_agent: bool = None,
                 is_screenshot: bool = None,
                 full_remote_path: str = None,
                 host: str = None,
                 task_id: int = None,
                 md5: str = None,
                 sha1: str = None,
                 timestamp: time = None,
                 cmd: str = None,
                 tags: list[str] = None,
                 complete: bool = None,
                 **kwargs):
        self.AgentFileId = agent_file_id
        self.Filename = filename
        self.Comment = comment
        self.IsPayload = is_payload
        self.IsDownloadFromAgent = is_download_from_agent
        self.IsScreenshot = is_screenshot
        self.FullRemotePath = full_remote_path
        self.Host = host
        self.TaskID = task_id
        self.Md5 = md5
        self.Sha1 = sha1
        self.Timestamp = timestamp
        self.Command = cmd
        self.Tags = tags
        self.Complete = complete
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")
    def to_json(self):
        return {
            "agent_file_id": self.AgentFileId,
            "filename": self.Filename,
            "comment": self.Comment,
            "is_payload": self.IsPayload,
            "is_download_from_agent": self.IsDownloadFromAgent,
            "is_screenshot": self.IsScreenshot,
            "full_remote_path": self.FullRemotePath,
            "host": self.Host,
            "task_id": self.TaskID,
            "md5": self.Md5,
            "sha1": self.Sha1,
            "timestamp": self.Timestamp,
            "cmd": self.Command,
            "tags": self.Tags,
            "complete": self.Complete
        }
class MythicRPCFileSearchMessageResponse:
    Success: bool
    Error: str
    Files: list[FileData]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 files: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Files = [FileData(**x) for x in files] if files is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCFileSearch(
        msg: MythicRPCFileSearchMessage) -> MythicRPCFileSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_FILE_SEARCH,
                                                                            body=msg.to_json())
    finalResponse = MythicRPCFileSearchMessageResponse(**response)
    return finalResponse
