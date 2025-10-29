import mythic_container
from mythic_container.logging import logger
from mythic_container.MythicGoRPC.send_mythic_rpc_callback_search import MythicRPCCallbackSearchMessageResult
import time

MYTHIC_RPC_CALLBACK_EDGE_SEARCH = "mythic_rpc_callback_edge_search"


class MythicRPCCallbackEdgeSearchMessage:
    """
    CallbackID or AgentCallbackID is required
    """
    def __init__(self,
                 AgentCallbackID: str = None,
                 CallbackID: int = None,
                 SearchC2ProfileName: str = None,
                 SearchActiveEdgesOnly: bool = False,
                 **kwargs):
        self.CallbackID = CallbackID
        self.AgentCallbackID = AgentCallbackID
        self.SearchC2ProfileName = SearchC2ProfileName
        self.SearchActiveEdgesOnly = SearchActiveEdgesOnly
        for k, v in kwargs.items():
            if k == "AgentCallbackUUID":
                self.AgentCallbackID = v
                logger.warning("MythicRPCCallbackEdgeSearchMessage using old API call, update AgentCallbackUUID to AgentCallbackID")
                continue
            if k == "AgentCallbackID":
                if isinstance(v, str):
                    self.AgentCallbackID = v
                if isinstance(v, int):
                    self.CallbackID = v
                    logger.warning("MythicRPCCallbackEdgeSearchMessage using old API call, update AgentCallbackID to CallbackID")
                continue
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "agent_callback_id": self.AgentCallbackID,
            "callback_id": self.CallbackID,
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

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 results: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Results: list[MythicRPCCallbackEdgeSearchMessageResult] =  []
        try:
            if success:
                for x in results:
                    source = MythicRPCCallbackSearchMessageResult(**x['source'])
                    destination = MythicRPCCallbackSearchMessageResult(**x['destination'])
                    self.Results.append(MythicRPCCallbackEdgeSearchMessageResult(
                        id=x['id'], c2profile=x['c2profile'], start_timestamp=x['start_timestamp'],
                        end_timestamp=x['end_timestamp'],
                        source=source, destination=destination,
                    ))
        except Exception as e:
            logger.error(e)
        #self.Results = [MythicRPCCallbackEdgeSearchMessageResult(**x) for x in results] if results is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackEdgeSearch(
        msg: MythicRPCCallbackEdgeSearchMessage) -> MythicRPCCallbackEdgeSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_EDGE_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCCallbackEdgeSearchMessageResponse(**response)
