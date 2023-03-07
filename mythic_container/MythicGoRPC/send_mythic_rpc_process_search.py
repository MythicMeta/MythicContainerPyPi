import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_PROCESS_SEARCH = "mythic_rpc_process_search"

class MythicRPCProcessSearchData:
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
                 Description: str = None,
                 Signer: str = None,
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
        self.Description = Description
        self.Signer = Signer
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
            "description": self.Description,
            "signer": self.Signer,
            **self.other
        }

class MythicRPCProcessSearchResponseData:
    def __init__(self,
                 host: str = None,
                 process_id: int = None,
                 parent_process_id: int = None,
                 architecture: str = None,
                 bin_path: str = None,
                 name: str = None,
                 user: str = None,
                 command_line: str = None,
                 integrity_level: int = None,
                 start_time: int = None,
                 description: str = None,
                 signer: str = None,
                 protection_process_level: int = None,
                 **kwargs):
        self.Host = host
        self.ProcessID = process_id
        self.ParentProcessID = parent_process_id
        self.Architecture = architecture
        self.BinPath = bin_path
        self.Name = name
        self.User = user
        self.CommandLine = command_line
        self.IntegrityLevel = integrity_level
        self.StartTime = start_time
        self.Description = description
        self.Signer = signer
        self.ProtectionProcessLevel = protection_process_level
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


class MythicRPCProcessesSearchMessage:
    def __init__(self,
                 TaskID: int,
                 Process: MythicRPCProcessSearchData = None,
                 **kwargs):
        self.TaskID = TaskID
        self.Process = Process
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "process": self.Process.to_json()
        }


class MythicRPCProcessesSearchMessageResponse:
    Processes: list[MythicRPCProcessSearchResponseData]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 processes: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Processes = [MythicRPCProcessSearchResponseData(**x) for x in processes] if processes is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCProcessSearch(
        msg: MythicRPCProcessesSearchMessage) -> MythicRPCProcessesSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_PROCESS_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCProcessesSearchMessageResponse(**response)
