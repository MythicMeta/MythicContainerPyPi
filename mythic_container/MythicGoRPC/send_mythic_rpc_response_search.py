import mythic_container
from mythic_container.logging import logger
import base64

MYTHIC_RPC_RESPONSE_SEARCH = "mythic_rpc_response_search"


class MythicRPCResponseSearchMessage:
    def __init__(self,
                 TaskID: int,
                 Response: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.Response = Response
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "response": self.Response
        }


class MythicRPCResponseSearchData:
    def __init__(self,
                 response_id: int = None,
                 response: str = None,
                 task_id: int = None,
                 **kwargs):
        self.ResponseID = response_id
        self.Response = base64.b64decode(response).decode()
        self.TaskID = task_id
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return{
            "id": self.ResponseID,
            "task_id": self.TaskID,
            "response": self.Response
        }

class MythicRPCResponseSearchMessageResponse:
    Responses: list[MythicRPCResponseSearchData]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 responses: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Responses = [MythicRPCResponseSearchData(**x) for x in responses] if responses is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCResponseSearch(
        msg: MythicRPCResponseSearchMessage) -> MythicRPCResponseSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_RESPONSE_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCResponseSearchMessageResponse(**response)
