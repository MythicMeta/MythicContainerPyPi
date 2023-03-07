import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_ARTIFACT_CREATE = "mythic_rpc_artifact_create"


class MythicRPCArtifactCreateMessage:
    def __init__(self,
                 TaskID: int,
                 ArtifactMessage: str,
                 BaseArtifactType: str,
                 ArtifactHost: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.ArtifactMessage = ArtifactMessage
        self.BaseArtifactType = BaseArtifactType
        self.ArtifactHost = ArtifactHost
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "message": self.ArtifactMessage,
            "base_artifact": self.BaseArtifactType,
            "host": self.ArtifactHost
        }


class MythicRPCArtifactCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCArtifactCreate(
        msg: MythicRPCArtifactCreateMessage) -> MythicRPCArtifactCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_ARTIFACT_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCArtifactCreateMessageResponse(**response)
