import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_CALLBACK_UPDATE = "mythic_rpc_callback_update"


class MythicRPCCallbackUpdateMessage:
    def __init__(self,
                 AgentCallbackID: str = None,
                 CallbackID: int = None,
                 TaskID: int = None,
                 EncryptionKeyBase64: str = None,
                 DecryptionKeyBase64: str = None,
                 CryptoType: str = None,
                 User: str = None,
                 Host: str = None,
                 PID: int = None,
                 ExtraInfo: str = None,
                 SleepInfo: str = None,
                 IP: str = None,
                 ExternalIP: str = None,
                 IntegrityLevel: int = None,
                 OS: str = None,
                 Domain: str = None,
                 Architecture: str = None,
                 Description: str = None,
                 ProcessName: str = None,
                 Cwd: str = None,
                 ImpersonationContext: str = None,
                 UpdateLastCheckinTime: bool = False,
                 UpdateLastCheckinTimeViaC2Profile: str = None,
                 Dead: bool = None,
                 **kwargs):
        self.AgentCallbackID = AgentCallbackID
        self.CallbackID = CallbackID
        self.TaskID = TaskID
        self.EncryptionKeyBase64 = EncryptionKeyBase64
        self.DecryptionKeyBase64 = DecryptionKeyBase64
        self.CryptoType = CryptoType
        self.User = User
        self.Host = Host
        self.PID = PID
        self.ExtraInfo = ExtraInfo
        self.SleepInfo = SleepInfo
        self.Ip = IP
        self.ExternalIP = ExternalIP
        self.IntegrityLevel = IntegrityLevel
        self.Os = OS
        self.Domain = Domain
        self.Architecture = Architecture
        self.Description = Description
        self.ProcessName = ProcessName
        self.Cwd = Cwd
        self.ImpersonationContext = ImpersonationContext
        self.UpdateLastCheckinTime = UpdateLastCheckinTime
        self.UpdateLastCheckinTimeViaC2Profile = UpdateLastCheckinTimeViaC2Profile
        self.Dead = Dead
        for k, v in kwargs.items():
            if k == "AgentCallbackUUID":
                self.AgentCallbackID = v
                logger.warning("MythicRPCCallbackUpdateMessage using old API call, update AgentCallbackUUID to AgentCallbackID")
                continue
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "agent_callback_id": self.AgentCallbackID,
            "callback_id": self.CallbackID,
            "task_id": self.TaskID,
            "encryption_key": self.EncryptionKeyBase64,
            "decryption_key": self.DecryptionKeyBase64,
            "crypto_type": self.CryptoType,
            "user": self.User,
            "host": self.Host,
            "pid": self.PID,
            "extra_info": self.ExtraInfo,
            "sleep_info": self.SleepInfo,
            "ip": self.Ip,
            "external_ip": self.ExternalIP,
            "integrity_level": self.IntegrityLevel,
            "os": self.Os,
            "domain": self.Domain,
            "architecture": self.Architecture,
            "description": self.Description,
            "process_name": self.ProcessName,
            "cwd": self.Cwd,
            "impersonation_context": self.ImpersonationContext,
            "update_last_checkin_time": self.UpdateLastCheckinTime,
            "update_last_checkin_time_via_c2_profile": self.UpdateLastCheckinTimeViaC2Profile,
            "dead": self.Dead,
        }


class MythicRPCCallbackUpdateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 **kwargs):
        self.Success = success
        self.Error = error
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackUpdate(
        msg: MythicRPCCallbackUpdateMessage) -> MythicRPCCallbackUpdateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_UPDATE,
                                                                            body=msg.to_json())
    return MythicRPCCallbackUpdateMessageResponse(**response)
