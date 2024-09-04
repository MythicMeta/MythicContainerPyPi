import mythic_container
from mythic_container.logging import logger
import base64

MYTHIC_RPC_CALLBACK_NEXT_CHECKIN_RANGE = "mythic_rpc_callback_next_checkin_range"


class MythicRPCCallbackNextCheckinRangeMessage:
    def __init__(self,
                 SleepInterval: int = None,
                 SleepJitter: int = None,
                 LastCheckin: str = None,
                 **kwargs):
        self.SleepInterval = SleepInterval
        self.SleepJitter = SleepJitter
        self.LastCheckin = LastCheckin
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "sleep_interval": self.SleepInterval,
            "sleep_jitter": self.SleepJitter,
            "last_checkin": self.LastCheckin,
        }


class MythicRPCCallbackNextCheckinRangeMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 min: str = "",
                 max: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Min = min
        self.Max = max
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "min": self.Min,
            "max": self.Max,
        }


async def SendMythicRPCCallbackNextCheckinRange(
        msg: MythicRPCCallbackNextCheckinRangeMessage) -> MythicRPCCallbackNextCheckinRangeMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
        queue=MYTHIC_RPC_CALLBACK_NEXT_CHECKIN_RANGE,
        body=msg.to_json())
    return MythicRPCCallbackNextCheckinRangeMessageResponse(**response)
