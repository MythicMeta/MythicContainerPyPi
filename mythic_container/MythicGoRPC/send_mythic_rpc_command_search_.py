import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_COMMAND_SEARCH = "mythic_rpc_command_search"

class MythicRPCCommandSearchMessage:
    def __init__(self,
                 SearchPayloadTypeName: str,
                 SearchCommandNames: list[str] = None,
                 SearchSupportedUIFeatures: str = None,
                 SearchScriptOnly: bool = None,
                 SearchAttributes: dict = None,
                 SearchOS: str = None,
                 **kwargs):
        self.SearchCommandNames = SearchCommandNames
        self.SearchOS = SearchOS
        self.SearchPayloadTypeName = SearchPayloadTypeName
        self.SearchSupportedUIFeatures = SearchSupportedUIFeatures
        self.SearchScriptOnly = SearchScriptOnly
        self.SearchAttributes = SearchAttributes
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "command_names": self.SearchCommandNames,
            "os": self.SearchOS,
            "payload_type_name": self.SearchPayloadTypeName,
            "supported_ui_features": self.SearchSupportedUIFeatures,
            "script_only": self.SearchScriptOnly,
            "params": self.SearchAttributes
        }


class MythicRPCCommandSearchData:
    def __init__(self,
                 cmd: str = None,
                 version: int = None,
                 attributes: dict = None,
                 needs_admin: bool = None,
                 help_cmd: str = None,
                 description: str = None,
                 supported_ui_features: list[str] = None,
                 author: str = None,
                 script_only: bool = None,
                 **kwargs):
        self.Name = cmd
        self.Version = version
        self.Attributes = attributes
        self.NeedsAdmin = needs_admin
        self.HelpCmd = help_cmd
        self.Description = description
        self.SupportedUiFeatures = supported_ui_features
        self.Author = author
        self.ScriptOnly = script_only
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "cmd": self.Name,
            "version": self.Version,
            "attributes": self.Attributes,
            "needs_admin": self.NeedsAdmin,
            "help_cmd": self.HelpCmd,
            "description": self.Description,
            "supported_ui_features": self.SupportedUiFeatures,
            "author": self.Author,
            "script_only": self.ScriptOnly
        }

class MythicRPCCommandSearchMessageResponse:
    Commands: list[MythicRPCCommandSearchData]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 commands: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Commands = [MythicRPCCommandSearchData(**x) for x in commands] if commands is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCommandSearch(
        msg: MythicRPCCommandSearchMessage) -> MythicRPCCommandSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_COMMAND_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCCommandSearchMessageResponse(**response)
