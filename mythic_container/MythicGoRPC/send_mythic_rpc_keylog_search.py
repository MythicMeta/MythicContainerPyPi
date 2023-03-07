import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_KEYLOG_SEARCH = "mythic_rpc_keylog_search"

class MythicRPCKeylogSearchData:
    def __init__(self,
                 WindowTitle: str = None,
                 User: bool = None,
                 Keystrokes: dict = None,
                 **kwargs):
        self.WindowTitle = WindowTitle
        self.User = User
        self.Keystrokes = Keystrokes
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "window_title": self.WindowTitle,
            "user": self.User,
            "keystrokes": self.Keystrokes,
        }

class MythicRPCKeylogSearchResultData:
    def __init__(self,
                 window_title: str = None,
                 user: bool = None,
                 keystrokes: dict = None,
                 **kwargs):
        self.WindowTitle = window_title
        self.User = user
        self.Keystrokes = keystrokes
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "window_title": self.WindowTitle,
            "user": self.User,
            "keystrokes": self.Keystrokes,
        }


class MythicRPCKeylogSearchMessage:
    def __init__(self,
                 TaskID: int,
                 Keylog: MythicRPCKeylogSearchData,
                 **kwargs):
        self.TaskID = TaskID
        self.Keylog = Keylog
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "keylogs": self.Keylog.to_json()
        }


class MythicRPCKeylogSearchMessageResponse:
    Keylogs: list[MythicRPCKeylogSearchResultData]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 keylogs: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Keylogs = [MythicRPCKeylogSearchResultData(**x) for x in keylogs] if keylogs is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCKeylogCreate(
        msg: MythicRPCKeylogSearchMessage) -> MythicRPCKeylogSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_KEYLOG_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCKeylogSearchMessageResponse(**response)
