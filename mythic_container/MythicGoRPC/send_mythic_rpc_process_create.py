import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_PROCESS_CREATE = "mythic_rpc_process_create"

class MythicRPCProcessCreateData:
    def __init__(self,
                 Host: str = None,
                 ProcessID: int = None,
                 ParentProcessID: int = None,
                 Architecture: str = None,
                 BinPath: str = None,
                 Name: str = None,
                 User: str = None,
                 CommandLine: str = None,
                 IntegrityLevel: int = None,
                 StartTime: int = None,
                 Description: str = None,
                 Signer: str = None,
                 ProtectionProcessLevel: int = None,
                 **kwargs):
        self.Host = Host
        self.ProcessID = ProcessID
        self.ParentProcessID = ParentProcessID
        self.Architecture = Architecture
        self.BinPath = BinPath
        self.Name = Name
        self.User = User
        self.CommandLine = CommandLine
        self.IntegrityLevel = IntegrityLevel
        self.StartTime = StartTime
        self.Description = Description
        self.Signer = Signer
        self.ProtectionProcessLevel = ProtectionProcessLevel
        self.other = kwargs

    def to_json(self):
        return {
            "host": self.Host,
            "process_id": self.ProcessID,
            "parent_process_id": self.ParentProcessID,
            "architecture": self.Architecture,
            "bin_path": self.BinPath,
            "name": self.Name,
            "user": self.User,
            "command_line": self.CommandLine,
            "integrity_level": self.IntegrityLevel,
            "start_time": self.StartTime,
            "description": self.Description,
            "signer": self.Signer,
            "protected_process_level": self.ProtectionProcessLevel,
            **self.other
        }


class MythicRPCProcessesCreateMessage:
    def __init__(self,
                 TaskID: int,
                 Processes: list[MythicRPCProcessCreateData] = None,
                 **kwargs):
        self.TaskID = TaskID
        self.Processes = Processes
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "processes": [x.to_json() for x in self.Processes]
        }


class MythicRPCProcessesCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCProcessCreate(
        msg: MythicRPCProcessesCreateMessage) -> MythicRPCProcessesCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_PROCESS_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCProcessesCreateMessageResponse(**response)
