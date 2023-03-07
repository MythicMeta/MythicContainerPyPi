import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_PAYLOAD_CREATE_FROM_SCRATCH = "mythic_rpc_payload_create_from_scratch"

class MythicRPCPayloadConfigurationC2Profile:
    def __init__(self,
                 Name: str = None,
                 Parameters: dict = None,
                 c2_profile: str = None,
                 c2_profile_parameters: dict = None,
                 **kwargs):
        self.Name = Name
        self.Parameters = Parameters
        if c2_profile is not None:
            self.Name = c2_profile
        if c2_profile_parameters is not None:
            self.Parameters = c2_profile_parameters
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return {
            "c2_profile": self.Name,
            "c2_profile_parameters": self.Parameters
        }
class MythicRPCPayloadConfigurationBuildParameter:
    def __init__(self,
                 Name: str = None,
                 Value: any = None,
                 name: str = None,
                 value: any = None,
                 **kwargs):
        self.Name = Name
        self.Value = Value
        if name is not None:
            self.Name = name
        if value is not None:
            self.Value = value
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return {
            "name": self.Name,
            "value": self.Value
        }
class MythicRPCPayloadConfiguration:
    def __init__(self,
                 Description: str = None,
                 PayloadType: str = None,
                 C2Profiles: list[MythicRPCPayloadConfigurationC2Profile] = None,
                 BuildParameters: list[MythicRPCPayloadConfigurationBuildParameter] = None,
                 Commands: list[str] = None,
                 SelectedOS: str = None,
                 Filename: str = None,
                 WrappedPayloadUUID: str = None,
                 UUID: str = None,
                 AgentFileId: str = None,
                 **kwargs):
        self.Description = Description
        self.PayloadType = PayloadType
        self.C2Profiles = C2Profiles
        self.BuildParameters = BuildParameters
        self.Commands = Commands
        self.SelectedOS = SelectedOS
        self.Filename = Filename
        self.WrappedPayloadUUID = WrappedPayloadUUID
        self.UUID = UUID
        self.AgentFileId = AgentFileId
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "description": self.Description,
            "payload_type": self.PayloadType,
            "c2_profiles": [x.to_json() for x in self.C2Profiles],
            "build_parameters": [x.to_json() for x in self.BuildParameters],
            "commands": self.Commands,
            "selected_os": self.SelectedOS,
            "filename": self.Filename,
            "wrapped_payload": self.WrappedPayloadUUID,
            "uuid": self.UUID,
            "agent_file_id": self.AgentFileId
        }


class MythicRPCPayloadCreateFromScratchMessage:
    def __init__(self,
                 TaskID: int,
                 PayloadConfiguration: MythicRPCPayloadConfiguration,
                 RemoteHost: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.PayloadConfiguration = PayloadConfiguration
        self.RemoteHost = RemoteHost
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "payload_configuration": self.PayloadConfiguration.to_json(),
            "remote_host": self.RemoteHost
        }


class MythicRPCPayloadCreateFromScratchMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 new_payload_uuid: str = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.NewPayloadUUID = new_payload_uuid
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCPayloadCreateFromScratch(
        msg: MythicRPCPayloadCreateFromScratchMessage) -> MythicRPCPayloadCreateFromScratchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_PAYLOAD_CREATE_FROM_SCRATCH,
                                                                            body=msg.to_json())

    return MythicRPCPayloadCreateFromScratchMessageResponse(**response)
