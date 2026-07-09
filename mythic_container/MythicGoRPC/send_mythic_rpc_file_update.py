import mythic_container
from mythic_container.logging import logger
import base64

MYTHIC_RPC_FILE_UPDATE = "mythic_rpc_file_update"


class MythicRPCFileUpdateMessage:
    def __init__(self,
                 AgentFileID: str,
                 Comment: str = None,
                 Filename: str = None,
                 AppendContents: bytes = None,
                 ReplaceContents: bytes = None,
                 Delete: bool = None,
                 DeleteAfterFetch: bool = None,
                 **kwargs):
        self.AgentFileID = AgentFileID
        self.Filename = Filename
        self.Comment = Comment
        self.AppendContents = AppendContents
        self.ReplaceContents = ReplaceContents
        self.Delete = Delete
        self.DeleteAfterFetch = DeleteAfterFetch
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def _serialize_contents(self, contents):
        if isinstance(contents, bytes):
            return base64.b64encode(contents).decode()
        return contents

    def to_json(self):
        return {
            "file_id": self.AgentFileID,
            "filename": self.Filename,
            "comment": self.Comment,
            "append_contents": self._serialize_contents(self.AppendContents),
            "replace_contents": self._serialize_contents(self.ReplaceContents),
            "delete": self.Delete,
            "delete_after_fetch": self.DeleteAfterFetch,
        }


class MythicRPCFileUpdateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCFileUpdate(
        msg: MythicRPCFileUpdateMessage) -> MythicRPCFileUpdateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_FILE_UPDATE,
                                                                            body=msg.to_json())
    return MythicRPCFileUpdateMessageResponse(**response)
