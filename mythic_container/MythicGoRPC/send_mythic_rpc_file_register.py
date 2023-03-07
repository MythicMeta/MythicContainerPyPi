import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_FILE_REGISTER = "mythic_rpc_file_register"


class MythicRPCFileRegisterMessage:
    def __init__(self,
                 OperationId: int,
                 OperatorId: int = None,
                 DeleteAfterFetch: bool = False,
                 Filename: str = None,
                 Comment: str = "",
                 **kwargs):
        self.DeleteAfterFetch = DeleteAfterFetch
        self.Filename = Filename
        self.Comment = Comment
        self.OperationId = OperationId
        self.OperatorId = OperatorId
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "delete_after_fetch": self.DeleteAfterFetch,
            "filename": self.Filename,
            "comment": self.Comment,
            "operation_id": self.OperationId,
            "operator_id": self.OperatorId
        }


class MythicRPCFileRegisterMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 agent_file_id: str = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.AgentFileId = agent_file_id
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCFileRegister(
        msg: MythicRPCFileRegisterMessage) -> MythicRPCFileRegisterMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_FILE_REGISTER,
                                                                            body=msg.to_json())
    finalResponse = MythicRPCFileRegisterMessageResponse(**response)
    return finalResponse
