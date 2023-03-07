import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_PAYLOAD_UPDATE_BUILD_STEP = "mythic_rpc_payload_update_build_step"


class MythicRPCPayloadUpdateBuildStepMessage:
    def __init__(self,
                 PayloadUUID: str,
                 StepName: str = "",
                 StepStdout: str = "",
                 StepStderr: str = "",
                 StepSuccess: bool = False,
                 **kwargs):
        self.PayloadUUID = PayloadUUID
        self.StepName = StepName
        self.StepStdout = StepStdout
        self.StepStderr = StepStderr
        self.StepSuccess = StepSuccess
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "payload_uuid": self.PayloadUUID,
            "step_name": self.StepName,
            "step_stdout": self.StepStdout,
            "step_stderr": self.StepStderr,
            "step_success": self.StepSuccess
        }


class MythicRPCPayloadUpdateBuildStepMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCPayloadUpdatebuildStep(
        msg: MythicRPCPayloadUpdateBuildStepMessage) -> MythicRPCPayloadUpdateBuildStepMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_PAYLOAD_UPDATE_BUILD_STEP,
                                                                            body=msg.to_json())
    return MythicRPCPayloadUpdateBuildStepMessageResponse(**response)