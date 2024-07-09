import mythic_container
from mythic_container.logging import logger
import base64

MYTHIC_RPC_FILEBROWSER_PARSE_PATH = "mythic_rpc_filebrowser_parse_path"


class MythicRPCFileBrowserParsePathMessage:
    def __init__(self,
                 Path: str = None,
                 **kwargs):
        self.Path = Path
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "path": self.Path,
        }

class AnalyzedPath:
    def __init__(self,
                 path_pieces: [str] = [],
                 path_separator: str = "",
                 host: str = ""):
        self.PathPieces = path_pieces
        self.PathSeparator = path_separator
        self.Host = host

    def to_json(self):
        return {
            "path_pieces": self.PathPieces,
            "path_separator": self.PathSeparator,
            "host": self.Host
        }
class MythicRPCFileBrowserParsePathMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 analyzed_path: dict = {},
                 **kwargs):
        self.Success = success
        self.Error = error
        self.AnalyzedPath = AnalyzedPath(**analyzed_path)
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "analyzed_path": self.AnalyzedPath.to_json(),
        }


async def SendMythicRPCFileBrowserParsePath(
        msg: MythicRPCFileBrowserParsePathMessage) -> MythicRPCFileBrowserParsePathMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
        queue=MYTHIC_RPC_FILEBROWSER_PARSE_PATH,
        body=msg.to_json())
    return MythicRPCFileBrowserParsePathMessageResponse(**response)
