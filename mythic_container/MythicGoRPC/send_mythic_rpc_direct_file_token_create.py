import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_DIRECT_FILE_TOKEN_CREATE = "mythic_rpc_direct_file_token_create"


class MythicRPCDirectFileTokenCreateMessage:
    def __init__(self,
                 AgentFileID: str = None,
                 Action: str = "download",
                 **kwargs):
        self.AgentFileID = AgentFileID
        self.Action = Action
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "agent_file_id": self.AgentFileID,
            "action": self.Action,
        }


class MythicRPCDirectFileTokenCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 token: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Token = token
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCDirectFileTokenCreate(
        msg: MythicRPCDirectFileTokenCreateMessage) -> MythicRPCDirectFileTokenCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
        queue=MYTHIC_RPC_DIRECT_FILE_TOKEN_CREATE,
        body=msg.to_json(),
    )
    return MythicRPCDirectFileTokenCreateMessageResponse(**response)
