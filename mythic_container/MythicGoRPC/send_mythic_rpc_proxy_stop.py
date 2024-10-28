import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_PROXY_STOP = "mythic_rpc_proxy_stop"


class MythicRPCProxyStopMessage:
    def __init__(self,
                 TaskID: int,
                 Port: int,
                 PortType: str,
                 Username: str = "",
                 Password: str = "",
                 **kwargs):
        self.TaskID = TaskID
        self.Port = Port
        self.PortType = PortType
        self.Username = Username
        self.Password = Password
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "port": self.Port,
            "port_type": self.PortType,
            "username": self.Username,
            "password": self.Password,
        }


class MythicRPCProxyStopMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 local_port: int = 0,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.LocalPort = local_port
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCProxyStopCommand(
        msg: MythicRPCProxyStopMessage) -> MythicRPCProxyStopMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_PROXY_STOP,
                                                                            body=msg.to_json())
    return MythicRPCProxyStopMessageResponse(**response)
