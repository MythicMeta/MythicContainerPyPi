import mythic_container
from mythic_container.logging import logger
import time

MYTHIC_RPC_CALLBACK_SEARCH = "mythic_rpc_callback_search"


class MythicRPCCallbackSearchMessage:
    def __init__(self,
                 AgentCallbackUUID: str = None,
                 AgentCallbackID: int = None,
                 SearchCallbackID: int = None,
                 SearchCallbackDisplayID: int = None,
                 SearchCallbackUUID: str = None,
                 SearchCallbackUser: str = None,
                 SearchCallbackHost: str = None,
                 SearchCallbackPID: int = None,
                 SearchCallbackExtraInfo: str = None,
                 SearchCallbackSleepInfo: str = None,
                 SearchCallbackIP: str = None,
                 SearchCallbackExternalIP: str = None,
                 SearchCallbackIntegrityLevel: int = None,
                 SearchCallbackOs: str = None,
                 SearchCallbackDomain: str = None,
                 SearchCallbackArchitecture: str = None,
                 SearchCallbackDescription: str = None,
                 **kwargs):
        self.AgentCallbackID = AgentCallbackID
        self.AgentCallbackUUID = AgentCallbackUUID
        self.SearchCallbackID = SearchCallbackID
        self.SearchCallbackDisplayID = SearchCallbackDisplayID
        self.SearchCallbackUUID = SearchCallbackUUID
        self.SearchCallbackUser = SearchCallbackUser
        self.SearchCallbackHost = SearchCallbackHost
        self.SearchCallbackPID = SearchCallbackPID
        self.SearchCallbackExtraInfo = SearchCallbackExtraInfo
        self.SearchCallbackSleepInfo = SearchCallbackSleepInfo
        self.SearchCallbackIP = SearchCallbackIP
        self.SearchCallbackExternalIP = SearchCallbackExternalIP
        self.SearchCallbackIntegrityLevel = SearchCallbackIntegrityLevel
        self.SearchCallbackOs = SearchCallbackOs
        self.SearchCallbackDomain = SearchCallbackDomain
        self.SearchCallbackArchitecture = SearchCallbackArchitecture
        self.SearchCallbackDescription = SearchCallbackDescription
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "agent_callback_id": self.AgentCallbackUUID,
            "callback_id": self.AgentCallbackID,
            "search_callback_id": self.SearchCallbackID,
            "search_callback_display_id": self.SearchCallbackDisplayID,
            "search_callback_uuid": self.SearchCallbackUUID,
            "user": self.SearchCallbackUser,
            "host": self.SearchCallbackHost,
            "pid": self.SearchCallbackPID,
            "extra_info": self.SearchCallbackExtraInfo,
            "sleep_info": self.SearchCallbackSleepInfo,
            "ip": self.SearchCallbackIP,
            "external_ip": self.SearchCallbackExternalIP,
            "integrity_level": self.SearchCallbackIntegrityLevel,
            "os": self.SearchCallbackOs,
            "domain": self.SearchCallbackDomain,
            "architecture": self.SearchCallbackArchitecture,
            "description": self.SearchCallbackDescription
        }


class MythicRPCCallbackSearchMessageResult:
    def __init__(self,
                 id: int = None,
                 display_id: int = None,
                 agent_callback_id: str = None,
                 init_callback: time = None,
                 last_checkin: time = None,
                 user: str = None,
                 host: str = None,
                 pid: int = None,
                 ip: str = None,
                 external_ip: str = None,
                 process_name: str = None,
                 description: str = None,
                 operator_id: int = None,
                 active: bool = None,
                 registered_payload_uuid: str = None,
                 integrity_level: int = None,
                 locked: bool = None,
                 locked_operator_id: int = None,
                 operation_id: int = None,
                 crypto_type: str = None,
                 dec_key: str = None,
                 enc_key: str = None,
                 os: str = None,
                 architecture: str = None,
                 domain: str = None,
                 extra_info: str = None,
                 sleep_info: str = None,
                 timestamp: time = None,
                 **kwargs):
        self.ID = id
        self.DisplayID = display_id
        self.AgentCallbackID = agent_callback_id
        self.InitCallback = init_callback
        self.LastCheckin = last_checkin
        self.User = user
        self.Host = host
        self.PID = pid
        self.Ip = ip
        self.ExternalIp = external_ip
        self.ProcessName = process_name
        self.Description = description
        self.OperatorID = operator_id
        self.Active = active
        self.RegisteredPayloadUUID = registered_payload_uuid
        self.IntegrityLevel = integrity_level
        self.Locked = locked
        self.LockedOperatorID = locked_operator_id
        self.OperationID = operation_id
        self.CryptoType = crypto_type
        self.DecKey = dec_key
        self.EncKey = enc_key
        self.Os = os
        self.Architecture = architecture
        self.Domain = domain
        self.ExtraInfo = extra_info
        self.SleepInfo = sleep_info
        self.Timestamp = timestamp
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return {
            "id": self.ID,
            "display_id": self.DisplayID,
            "agent_callback_id": self.AgentCallbackID,
            "init_callback": self.InitCallback,
            "last_checkin": self.LastCheckin,
            "user": self.User,
            "host": self.Host,
            "pid": self.PID,
            "ip": self.Ip,
            "external_ip": self.ExternalIp,
            "process_name": self.ProcessName,
            "description": self.Description,
            "operator_id": self.OperatorID,
            "active": self.Active,
            "registered_payload_uuid": self.RegisteredPayloadUUID,
            "integrity_level": self.IntegrityLevel,
            "locked": self.Locked,
            "locked_operator_id": self.LockedOperatorID,
            "operation_id": self.OperationID,
            "crypto_type": self.CryptoType,
            "dec_key": self.DecKey,
            "enc_key": self.EncKey,
            "os": self.Os,
            "architecture": self.Architecture,
            "domain": self.Domain,
            "extra_info": self.ExtraInfo,
            "sleep_info": self.SleepInfo,
            "timestamp": self.Timestamp
        }


class MythicRPCCallbackSearchMessageResponse:
    Results: list[MythicRPCCallbackSearchMessageResult]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 results: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Results = [MythicRPCCallbackSearchMessageResult(**x) for x in results] if results is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCallbackSearch(
        msg: MythicRPCCallbackSearchMessage) -> MythicRPCCallbackSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CALLBACK_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCCallbackSearchMessageResponse(**response)
