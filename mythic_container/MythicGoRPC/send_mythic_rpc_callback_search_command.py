import mythic_container
from mythic_container.logging import logger
from .send_mythic_rpc_command_search_ import MythicRPCCommandSearchData

MYTHIC_RPC_CALLBACK_SEARCH_COMMAND = "mythic_rpc_callback_search_command"


class MythicRPCCallbackSearchCommandMessage:
    def __init__(self,
                 CallbackID: int = None,
                 TaskID: int = None,
                 SearchCommandNames: str = None,
                 SearchSupportedUIFeatures: str = None,
                 SearchScriptOnly: bool = None,
                 SearchAttributes: dict = None,
                 **kwargs):
        self.SearchCommandNames = SearchCommandNames
        self.CallbackID = CallbackID
        self.TaskID = TaskID
        self.SearchSupportedUIFeatures = SearchSupportedUIFeatures
        self.SearchScriptOnly = SearchScriptOnly
        self.SearchAttributes = SearchAttributes
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "command_names": self.SearchCommandNames,
            "supported_ui_features": self.SearchSupportedUIFeatures,
            "script_only": self.SearchScriptOnly,
            "params": self.SearchAttributes,
            "callback_id": self.CallbackID,
            "task_id": self.TaskID
        }


class MythicRPCCallbackSearchCommandMessageResponse:
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


async def SendMythicRPCCallbackSearchCommand(
        msg: MythicRPCCallbackSearchCommandMessage) -> MythicRPCCallbackSearchCommandMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_SEARCH_COMMAND,
                                                                            body=msg.to_json())
    return MythicRPCCallbackSearchCommandMessageResponse(**response)
