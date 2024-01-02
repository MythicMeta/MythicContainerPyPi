import mythic_container
from mythic_container.logging import logger
from mythic_container.MythicGoRPC.send_mythic_rpc_callback_search import MythicRPCCallbackSearchMessageResult
import time

MYTHIC_RPC_CALLBACK_EDGE_SEARCH = "mythic_rpc_callback_edge_search"


class MythicRPCCallbackEdgeSearchMessage:
    def __init__(self,
                 AgentCallbackUUID: str = None,
                 AgentCallbackID: int = None,
                 SearchC2ProfileName: str = None,
                 SearchActiveEdgesOnly: bool = False,
                 **kwargs):
        self.AgentCallbackID = AgentCallbackID
        self.AgentCallbackUUID = AgentCallbackUUID
        self.SearchC2ProfileName = SearchC2ProfileName
        self.SearchActiveEdgesOnly = SearchActiveEdgesOnly
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "agent_callback_id": self.AgentCallbackUUID,
            "callback_id": self.AgentCallbackID,
            "search_c2_profile_name": self.SearchC2ProfileName,
            "search_active_edges_only": self.SearchActiveEdgesOnly,
        }


class MythicRPCCallbackEdgeSearchMessageResult:
    def __init__(self,
                 source: MythicRPCCallbackSearchMessageResult,
                 destination: MythicRPCCallbackSearchMessageResult,
                 c2profile: str,
                 id: int = None,
                 start_timestamp: str = None,
                 end_timestamp: str = None,
                 **kwargs):
        self.ID = id
        self.StartTimestamp = start_timestamp
        self.EndTimestamp = end_timestamp
        self.Source = source
        self.Destination = destination
        self.C2ProfileName = c2profile

        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "start_timestamp": self.StartTimestamp,
            "end_timestamp": self.EndTimestamp,
            "source": self.Source.to_json(),
            "destination": self.Destination.to_json(),
            "c2profile": self.C2ProfileName,
        }


class MythicRPCCallbackEdgeSearchMessageResponse:
    Results: list[MythicRPCCallbackEdgeSearchMessageResult]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 results: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Results = [MythicRPCCallbackEdgeSearchMessageResult(**x) for x in results] if results is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackEdgeSearch(
        msg: MythicRPCCallbackEdgeSearchMessage) -> MythicRPCCallbackEdgeSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_EDGE_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCCallbackEdgeSearchMessageResponse(**response)
