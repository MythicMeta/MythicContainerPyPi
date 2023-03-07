import mythic_container
from mythic_container.logging import logger
import base64

MYTHIC_RPC_AGENTSTORAGE_SEARCH = "mythic_rpc_agentstorage_search"


class MythicRPCAgentStorageSearchMessage:
    def __init__(self,
                 SearchUniqueID: str,
                 **kwargs):
        self.SearchUniqueID = SearchUniqueID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "unique_id": self.SearchUniqueID
        }


class MythicRPCAgentStorageSearchResult:
    def __init__(self,
                 unique_id: str = "",
                 data: str = "",
                 **kwargs):
        self.UniqueID = unique_id
        self.Data = base64.b64decode(data)
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


class MythicRPCAgentStorageSearchMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 agentstorage_messages: [MythicRPCAgentStorageSearchResult] = [],
                 **kwargs):
        self.Success = success
        self.Error = error
        self.AgentStorageMessages = agentstorage_messages
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCAgentStorageSearch(
        msg: MythicRPCAgentStorageSearchMessage) -> MythicRPCAgentStorageSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_AGENTSTORAGE_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCAgentStorageSearchMessageResponse(**response)
