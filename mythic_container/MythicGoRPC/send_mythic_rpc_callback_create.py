import mythic_container
from mythic_container.logging import logger
import base64

MYTHIC_RPC_CALLBACK_CREATE = "mythic_rpc_callback_create"


class MythicRPCCallbackCreateMessage:
    def __init__(self,
                 PayloadUUID: str,
                 C2ProfileName: str,
                 EncryptionKey: bytes = None,
                 EncryptionKeyBase64: str = None,
                 DecryptionKey: bytes = None,
                 DecryptionKeyBase64: str = None,
                 CryptoType: str = "",
                 User: str = "",
                 Host: str = "",
                 PID: int = 0,
                 ExtraInfo: str = "",
                 SleepInfo: str = "",
                 Ip: str = "",
                 ExternalIP: str = "",
                 IntegrityLevel: int = 2,
                 Os: str = "",
                 Domain: str = "",
                 Architecture: str = "",
                 **kwargs):
        self.PayloadUUID = PayloadUUID
        self.C2ProfileName = C2ProfileName
        if EncryptionKey is not None:
            self.EncryptionKeyBase64 = base64.b64encode(EncryptionKey).decode()
        else:
            self.EncryptionKeyBase64 = EncryptionKeyBase64
        if DecryptionKey is not None:
            self.DecryptionKeyBase64 = base64.b64encode(DecryptionKey).decode()
        else:
            self.DecryptionKeyBase64 = DecryptionKeyBase64
        self.CryptoType = CryptoType
        self.User = User
        self.Host = Host
        self.PID = PID
        self.ExtraInfo = ExtraInfo
        self.SleepInfo = SleepInfo
        self.Ip = Ip
        self.ExternalIP = ExternalIP
        self.IntegrityLevel = IntegrityLevel
        self.Os = Os
        self.Domain = Domain
        self.Architecture = Architecture
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "payload_uuid": self.PayloadUUID,
            "c2_profile": self.C2ProfileName,
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
            "architecture": self.Architecture
        }


class MythicRPCCallbackCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 callback_uuid: str = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.CallbackUUID = callback_uuid
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackCreate(
        msg: MythicRPCCallbackCreateMessage) -> MythicRPCCallbackCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCCallbackCreateMessageResponse(**response)
