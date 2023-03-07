import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_ARTIFACT_SEARCH = "mythic_rpc_artifact_search"


class MythicRPCArtifactSearchArtifactData:
    def __init__(self,
                 host: str = None,
                 artifact_type: str = None,
                 artifact_message: str = None,
                 task_id: int = None,
                 **kwargs):
        self.Host = host
        self.ArtifactType = artifact_type
        self.ArtifactMessage = artifact_message
        self.TaskID = task_id
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "host": self.Host,
            "artifact_type": self.ArtifactType,
            "artifact_message": self.ArtifactMessage,
            "task_id": self.TaskID
        }


class MythicRPCArtifactSearchMessage:
    def __init__(self,
                 TaskID: int,
                 SearchArtifacts: MythicRPCArtifactSearchArtifactData,
                 **kwargs):
        self.TaskID = TaskID
        self.SearchArtifacts = SearchArtifacts
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "artifact": self.SearchArtifacts.to_json()
        }


class MythicRPCArtifactSearchMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 artifacts: [dict] = [],
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Artifacts = [MythicRPCArtifactSearchArtifactData(**x) for x in artifacts]
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCArtifactSearch(
        msg: MythicRPCArtifactSearchMessage) -> MythicRPCArtifactSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_ARTIFACT_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCArtifactSearchMessageResponse(**response)
