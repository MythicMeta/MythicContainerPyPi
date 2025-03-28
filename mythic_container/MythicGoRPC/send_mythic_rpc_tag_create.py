import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_TAG_CREATE = "mythic_rpc_tag_create"


class MythicRPCTagCreateMessage:
    def __init__(self,
                 TagTypeID: int,
                 URL: str = "",
                 Source: str = "",
                 Data: dict = None,
                 TaskID: int = None,
                 FileID: int = None,
                 CredentialID: int = None,
                 MythicTreeID: int = None,
                 **kwargs):
        self.TagTypeID = TagTypeID
        self.URL = URL
        self.Source = Source
        self.Data = Data if Data is not None else {}
        self.TaskID = TaskID
        self.FileID = FileID
        self.CredentialID = CredentialID
        self.MythicTreeID = MythicTreeID
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "tagtype_id": self.TagTypeID,
            "url": self.URL,
            "source": self.Source,
            "data": self.Data,
            "task_id": self.TaskID,
            "file_id": self.FileID,
            "credential_id": self.CredentialID,
            "mythic_tree_id": self.MythicTreeID
        }


class MythicRPCTagTypeData:
    def __init__(self,
                 id: int = None,
                 name: str = "",
                 description: str = "",
                 color: str = "",
                 operation_id: int = None,
                 **kwargs):
        self.ID = id
        self.Name = name
        self.Description = description
        self.Color = color
        self.OperationID = operation_id
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "name": self.Name,
            "description": self.Description,
            "color": self.Color,
            "operation_id": self.OperationID
        }


class MythicRPCTagData:
    def __init__(self,
                 id: int = None,
                 tagtype_id: int = None,
                 tagtype: dict = None,
                 data: dict = None,
                 url: str = "",
                 source: str = "",
                 task_id: int = None,
                 file_id: int = None,
                 credential_id: int = None,
                 mythic_tree_id: int = None,
                 **kwargs):
        self.ID = id
        self.TagTypeID = tagtype_id
        self.TagType = MythicRPCTagTypeData(**tagtype) if tagtype is not None else None
        self.Data = data if data is not None else {}
        self.URL = url
        self.Source = source
        self.TaskID = task_id
        self.FileID = file_id
        self.CredentialID = credential_id
        self.MythicTreeID = mythic_tree_id
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "tagtype_id": self.TagTypeID,
            "tagtype": self.TagType.to_json() if self.TagType is not None else None,
            "data": self.Data,
            "url": self.URL,
            "source": self.Source,
            "task_id": self.TaskID,
            "file_id": self.FileID,
            "credential_id": self.CredentialID,
            "mythic_tree_id": self.MythicTreeID
        }


class MythicRPCTagCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 tag: dict = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Tag = MythicRPCTagData(**tag) if tag is not None else None
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCTagCreate(
        msg: MythicRPCTagCreateMessage) -> MythicRPCTagCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TAG_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCTagCreateMessageResponse(**response)