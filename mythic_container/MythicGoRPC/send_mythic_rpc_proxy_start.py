import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_PROXY_START = "mythic_rpc_proxy_start"

CALLBACK_PORT_TYPE_SOCKS = "socks"
CALLBACK_PORT_TYPE_RPORTFWD = "rpfwd"
CALLBACK_PORT_TYPE_INTERACTIVE = "interactive"


class MythicRPCProxyStartMessage:
    """
    Start a new proxy session with Mythic.
    For PortType == CALLBACK_PORT_TYPE_SOCKS:
        LocalPort is used to open up a port on Mythic
    For PortType == CALLBACK_PORT_TYPE_RPORTFWD:
        LocalPort is used to open up a port on the host where the agent is running
        RemoteIP:RemotePort is used for Mythic to connect to when LocalPort gets a connection
    """

    def __init__(self,
                 TaskID: int,
                 PortType: str,
                 LocalPort: int = None,
                 RemotePort: int = None,
                 RemoteIP: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.LocalPort = LocalPort
        self.RemotePort = RemotePort
        self.RemoteIP = RemoteIP
        self.PortType = PortType
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "local_port": self.LocalPort,
            "remote_port": self.RemotePort,
            "remote_ip": self.RemoteIP,
            "port_type": self.PortType
        }


class MythicRPCProxyStartMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCProxyStartCommand(
        msg: MythicRPCProxyStartMessage) -> MythicRPCProxyStartMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_PROXY_START,
                                                                            body=msg.to_json())
    return MythicRPCProxyStartMessageResponse(**response)
