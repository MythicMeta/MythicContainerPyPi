import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_CREDENTIAL_SEARCH = "mythic_rpc_credential_search"


class MythicRPCCredentialData:
    def __init__(self,
                 credential_type: str = None,
                 realm: str = None,
                 account: str = None,
                 credential: str = None,
                 comment: str = None,
                 metadata: str = None,
                 **kwargs):
        self.CredentialType = credential_type
        self.Realm = realm
        self.Account = account
        self.Credential = credential
        self.Comment = comment
        self.ExtraData = metadata
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return {
            "credential_type": self.CredentialType,
            "realm": self.Realm,
            "account": self.Account,
            "credential": self.Credential,
            "comment": self.Comment,
            "metadata": self.ExtraData
        }

class MythicRPCCredentialSearchMessage:
    def __init__(self,
                 TaskID: int,
                 Credential: MythicRPCCredentialData = None,
                 **kwargs):
        self.TaskID = TaskID
        self.Credential = Credential
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "credentials": self.Credential.to_json() if self.Credential is not None else None
        }


class MythicRPCCredentialSearchMessageResponse:
    Credentials: list[MythicRPCCredentialData]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 credentials: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Credentials = [MythicRPCCredentialData(**x) for x in credentials] if credentials is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCCredentialSearch(
        msg: MythicRPCCredentialSearchMessage) -> MythicRPCCredentialSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_CREDENTIAL_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCCredentialSearchMessageResponse(**response)
