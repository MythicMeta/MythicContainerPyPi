import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_FILEBROWSER_CREATE = "mythic_rpc_filebrowser_create"

class MythicRPCFileBrowserDataChildren:
    def __init__(self,
                 IsFile: bool = None,
                 Permissions: dict = None,
                 Name: str = None,
                 AccessTime: int = None,
                 ModifyTime: int = None,
                 Size: int = None,
                 **kwargs):
        self.IsFile = IsFile
        self.Permissions = Permissions
        self.Name = Name
        self.AccessTime = AccessTime
        self.ModifyTime = ModifyTime
        self.Size = Size
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return {
            "is_file": self.IsFile,
            "permissions": self.Permissions,
            "name": self.Name,
            "access_time": self.AccessTime,
            "modify_time": self.ModifyTime,
            "size": self.Size
        }
class MythicRPCFileBrowserData:
    def __init__(self,
                 Host: str = None,
                 IsFile: bool = None,
                 Permissions: dict = None,
                 Name: str = None,
                 ParentPath: str = None,
                 Success: bool = None,
                 AccessTime: int = None,
                 ModifyTime: int = None,
                 Size: int = None,
                 UpdateDeleted: bool = None,
                 Files: list[MythicRPCFileBrowserDataChildren] = None,
                 **kwargs):
        self.Host = Host
        self.IsFile = IsFile
        self.Permissions = Permissions
        self.Name = Name
        self.ParentPath = ParentPath
        self.Success = Success
        self.AccessTime = AccessTime
        self.ModifyTime = ModifyTime
        self.Size = Size
        self.UpdateDeleted = UpdateDeleted
        self.Files = Files
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "host": self.Host,
            "is_file": self.IsFile,
            "permissions": self.Permissions,
            "name": self.Name,
            "parent_path": self.ParentPath,
            "success": self.Success,
            "access_time": self.AccessTime,
            "modify_time": self.ModifyTime,
            "size": self.Size,
            "update_deleted": self.UpdateDeleted,
            "files": [x.to_json() for x in self.Files]
        }


class MythicRPCFileBrowserCreateMessage:
    def __init__(self,
                 TaskID: int,
                 FileBrowser: MythicRPCFileBrowserData,
                 **kwargs):
        self.TaskID = TaskID
        self.FileBrowser = FileBrowser
        for k, v in kwargs:
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "callbacktokens": self.FileBrowser.to_json()
        }


class MythicRPCFileBrowserCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCFileBrowserCreate(
        msg: MythicRPCFileBrowserCreateMessage) -> MythicRPCFileBrowserCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_FILEBROWSER_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCFileBrowserCreateMessageResponse(**response)
