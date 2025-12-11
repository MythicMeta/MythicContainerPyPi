import mythic_container
from mythic_container.logging import logger
import time

MYTHIC_RPC_CUSTOMBROWSER_SEARCH = "mythic_rpc_custombrowser_search"

class MythicRPCCustomBrowserSearchData:
    def __init__(self,
                 TreeType: str,
                 Host: str,
                 Name: str = None,
                 ParentPath: str = None,
                 FullPath: str = None,
                 MetadataKey: str = None,
                 MetadataValue = None,
                 CallbackGroup: str = None,
                 ):
        self.TreeType = TreeType
        self.Host = Host
        self.Name = Name
        self.ParentPath = ParentPath
        self.FullPath = FullPath
        self.MetadataKey = MetadataKey
        self.MetadataValue = MetadataValue
        self.CallbackGroup = CallbackGroup
    def to_json(self):
        return {
            "tree_type": self.TreeType,
            "host": self.Host,
            "name": self.Name,
            "parent_path": self.ParentPath,
            "full_path": self.FullPath,
            "metadata_key": self.MetadataKey,
            "metadata_value": self.MetadataValue,
            "callback_group": self.CallbackGroup
        }
class MythicRPCCustomBrowserSearchMessage:
    def __init__(self,
                 TaskID: int = None,
                 OperationID: int = None,
                 GetAllMatchingChildren: bool = False,
                 SearchCustomBrowser: MythicRPCCustomBrowserSearchData = None):
        self.TaskID = TaskID
        self.OperationID = OperationID
        self.GetAllMatchingChildren = GetAllMatchingChildren
        self.SearchCustomBrowser = SearchCustomBrowser

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "operation_id": self.OperationID,
            "all_matching_children": self.GetAllMatchingChildren,
            "custombrowser": self.SearchCustomBrowser.to_json() if self.SearchCustomBrowser is not None else None
        }
class MythicRPCCustomBrowserSearchDataResponse:
    def __init__(self,
                 tree_type: str,
                 host: str = "",
                 name: str = "",
                 parent_path: str = "",
                 full_path: str = "",
                 metadata: dict = {}):
        self.TreeType = tree_type
        self.Host = host
        self.Name = name
        self.ParentPath = parent_path
        self.FullPath = full_path
        self.Metadata = metadata
    def to_json(self):
        return {
            "tree_type": self.TreeType,
            "host": self.Host,
            "name": self.Name,
            "parent_path": self.ParentPath,
            "full_path": self.FullPath,
            "metadata": self.Metadata
        }
class MythicRPCCustomBrowserSearchMessageResponse:
    CustomBrowser: list[MythicRPCCustomBrowserSearchDataResponse]
    def __init__(self,
                 success: bool = False,
                 error: str = None,
                 custombrowser: list[dict] = None,):
        self.Success = success
        self.Error = error
        self.CustomBrowser = [MythicRPCCustomBrowserSearchDataResponse(**x) for x in custombrowser] if custombrowser is not None else []
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "custombrowser": [x.to_json() for x in self.CustomBrowser]
        }



async def SendMythicRPCCustomBrowserSearch(
        msg: MythicRPCCustomBrowserSearchMessage) -> MythicRPCCustomBrowserSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CUSTOMBROWSER_SEARCH,
                                                                            body=msg.to_json())
    finalResponse = MythicRPCCustomBrowserSearchMessageResponse(**response)
    return finalResponse
