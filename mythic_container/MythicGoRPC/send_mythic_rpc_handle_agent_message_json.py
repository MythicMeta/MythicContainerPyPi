import mythic_container
from mythic_container.logging import logger
from mythic_container.MythicGoRPC.send_mythic_rpc_callback_search import MythicRPCCallbackSearchMessageResult
import time

MYTHIC_RPC_HANDLE_AGENT_MESSAGE_JSON = "mythic_rpc_handle_agent_message_json"

class MythicRPCHandleAgentMessageJsonMessage:
    """
    Must provide either CallbackID or AgentCallbackID 
    """
    def __init__(self,
                 CallbackID: int = None,
                 AgentCallbackID: str = None,
                 AgentMessage: dict = {},
                 UpdateCheckinTime: bool = False,
                 **kwargs):
        self.CallbackID = CallbackID
        self.AgentCallbackID = AgentCallbackID
        self.AgentMessage = AgentMessage
        self.UpdateCheckinTime = UpdateCheckinTime
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "callback_id": self.CallbackID,
            "agent_callback_id": self.AgentCallbackID,
            "agent_message": self.AgentMessage,
            "update_checkin_time": self.UpdateCheckinTime,
        }

class MythicRPCHandleAgentMessageJsonMessageResponse:

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 agent_response: dict = {},
                 **kwargs):
        self.Success = success
        self.Error = error
        self.AgentResponse = agent_response
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCHandleAgentMessageJson(
        msg: MythicRPCHandleAgentMessageJsonMessage) -> MythicRPCHandleAgentMessageJsonMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_HANDLE_AGENT_MESSAGE_JSON,
                                                                            body=msg.to_json())
    return MythicRPCHandleAgentMessageJsonMessageResponse(**response)
