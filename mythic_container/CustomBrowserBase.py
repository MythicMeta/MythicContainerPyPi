from collections.abc import Callable, Awaitable
from enum import Enum
from typing import List

import mythic_container
from .logging import logger

from .SharedClasses import ContainerOnStartMessage, ContainerOnStartMessageResponse

class ExportFunctionMessage:
    def __init__(self,
                 tree_type: str,
                 container_name: str,
                 host: str,
                 path: str,
                 operation_id: int,
                 operator_id: int,
                 operator_username: str,
                 callback_group: str,):
        self.TreeType = tree_type
        self.ContainerName = container_name
        self.Host = host
        self.Path = path
        self.OperationID = operation_id
        self.OperatorID = operator_id
        self.OperatorUsername = operator_username
        self.CallbackGroup = callback_group
    def to_json(self) -> dict:
        return {
            "tree_type": self.TreeType,
            "container_name": self.ContainerName,
            "host": self.Host,
            "path": self.Path,
            "operation_id": self.OperationID,
            "callback_group": self.CallbackGroup,
            "operator_id": self.OperatorID,
            "operator_username": self.OperatorUsername,
        }
class ExportFunctionMessageResponse:
    def __init__(self,
                 Success: bool = False,
                 Error: str = "",
                 CompletionMessage: str = "",
                 OperationID: int = 0,
                 TreeType: str = "",
                 ):
        self.Success = Success
        self.Error = Error
        self.CompletionMessage = CompletionMessage
        self.OperationID = OperationID
        self.TreeType = TreeType
    def to_json(self) -> dict:
        return {
            "success": self.Success,
            "error": self.Error,
            "completion_message": self.CompletionMessage,
            "operation_id": self.OperationID,
            "tree_type": self.TreeType,
        }
class CustomBrowserTableColumnType(str, Enum):
    String = "string"
    Date = "date"
    Number = "number"
    Size = "size"

class CustomBrowserTableColumn:
    def __init__(self,
                 Key: str,
                 Name: str,
                 FillWidth: bool = False,
                 Width: int = 0,
                 DisableSort: bool = False,
                 DisableDoubleClick: bool = False,
                 DisableFilterMenu: bool = False,
                 ColumnType: CustomBrowserTableColumnType = CustomBrowserTableColumnType.String):
        self.Key = Key
        self.Name = Name
        self.FillWidth = FillWidth
        self.Width = Width
        self.DisableSort = DisableSort
        self.DisableDoubleClick = DisableDoubleClick
        self.DisableFilterMenu = DisableFilterMenu
        self.ColumnType = ColumnType
    def to_json(self) -> dict:
        return {
            "key": self.Key,
            "name": self.Name,
            "fillWidth": self.FillWidth,
            "width": self.Width,
            "disableSort": self.DisableSort,
            "disableDoubleClick": self.DisableDoubleClick,
            "disableFilterMenu": self.DisableFilterMenu,
            "type": self.ColumnType
        }
class CustomBrowserRowAction:
    def __init__(self,
                 Name: str = "",
                 UIFeature: str = "",
                 Icon: str = "",
                 Color: str = "",
                 SupportsFile: bool = False,
                 SupportsFolder: bool = False,
                 OpenDialog: bool = False,
                 GetConfirmation: bool = False):
        self.Name = Name
        self.UIFeature = UIFeature
        self.Icon = Icon
        self.Color = Color
        self.SupportsFile = SupportsFile
        self.SupportsFolder = SupportsFolder
        self.OpenDialog = OpenDialog
        self.GetConfirmation = GetConfirmation
    def to_json(self) -> dict:
        return {
            "name": self.Name,
            "ui_feature": self.UIFeature,
            "icon": self.Icon,
            "color": self.Color,
            "supports_file": self.SupportsFile,
            "supports_folder": self.SupportsFolder,
            "openDialog": self.OpenDialog,
            "getConfirmation": self.GetConfirmation
        }
class CustomBrowserExtraTableTaskingInput:
    def __init__(self,
                 Name: str,
                 Description: str,
                 DisplayName: str,
                 Required: bool = False):
        self.Name = Name
        self.Description = Description
        self.DisplayName = DisplayName
        self.Required = Required
    def to_json(self) -> dict:
        return {
            "name": self.Name,
            "description": self.Description,
            "display_name": self.DisplayName,
            "required": self.Required
        }
class CustomBrowserType(str, Enum):
    """Types of custom browser views available
    """
    File = "file"

class CustomBrowser:
    """The base definition for a custom browser

    """
    name: str = ""
    description: str = ""
    author: str = ""
    semver: str = ""
    type: CustomBrowserType = CustomBrowserType.File
    path_separator: str = ""
    columns: List[CustomBrowserTableColumn] = []
    default_visible_columns: List[str] = []
    indicate_partial_listing: bool = False
    show_current_path: bool = False
    row_actions: List[CustomBrowserRowAction] = []
    extra_table_inputs: List[CustomBrowserExtraTableTaskingInput] = []
    export_function: Callable[
        [ExportFunctionMessage], Awaitable[ExportFunctionMessageResponse]] = None,

    async def on_container_start(self, message: ContainerOnStartMessage) -> ContainerOnStartMessageResponse:
        return ContainerOnStartMessageResponse(ContainerName=self.name)

    def get_sync_message(self):
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "semver": self.semver,
            "author": self.author,
            "separator": self.path_separator,
            "columns": [x.to_json() for x in self.columns],
            "default_visible_columns": self.default_visible_columns,
            "indicate_partial_listing": self.indicate_partial_listing,
            "show_current_path": self.show_current_path,
            "row_actions": [x.to_json() for x in self.row_actions],
            "extra_table_inputs": [x.to_json() for x in self.extra_table_inputs],
            "export_function": "function exists" if self.export_function is not None else ""
        }


custombrowsers: dict[str, CustomBrowser] = {}


async def SendMythicRPCSyncCustomBrowser(custombrowser_name: str) -> bool:
    try:
        custombrowser_services = CustomBrowser.__subclasses__()
        for cls in custombrowser_services:
            web = cls()
            if web.name == "":
                continue
            if web.name == custombrowser_name:
                custombrowsers.pop(custombrowser_name, None)
                custombrowsers[web.name] = web
                await mythic_container.mythic_service.syncCustomBrowserData(web)
                return True
        return False
    except Exception as e:
        return False
