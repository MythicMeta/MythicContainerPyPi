import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_C2_UPDATE_STATUS = "mythic_rpc_c2_update_status"


class MythicRPCC2UpdateStatusMessage:
    """
    Update a C2 profile's status on the Mythic server about if the internal server is running or not
    """

    def __init__(self,
                 C2Profile: str,
                 InternalServerRunning: bool,
                 Error: str = None,
                 **kwargs):
        self.C2Profile = C2Profile
        self.InternalServerRunning = InternalServerRunning
        self.Error = Error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "c2_profile": self.C2Profile,
            "server_running": self.InternalServerRunning,
            "error": self.Error,
        }


class MythicRPCC2UpdateStatusMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCC2UpdateStatus(
        msg: MythicRPCC2UpdateStatusMessage) -> MythicRPCC2UpdateStatusMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_C2_UPDATE_STATUS,
                                                                            body=msg.to_json())
    return MythicRPCC2UpdateStatusMessageResponse(**response)
