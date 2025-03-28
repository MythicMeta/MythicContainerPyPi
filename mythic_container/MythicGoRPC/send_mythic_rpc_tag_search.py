import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_TAG_SEARCH = "mythic_rpc_tag_search"


class MythicRPCTagSearchMessage:
    def __init__(self,
                 TaskID: int,
                 SearchTagID: int = None,
                 SearchTagTaskID: int = None,
                 SearchTagFileID: int = None,
                 SearchTagCredentialID: int = None,
                 SearchTagMythicTreeID: int = None,
                 SearchTagSource: str = None,
                 SearchTagData: str = None,
                 SearchTagURL: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.SearchTagID = SearchTagID
        self.SearchTagTaskID = SearchTagTaskID
        self.SearchTagFileID = SearchTagFileID
        self.SearchTagCredentialID = SearchTagCredentialID
        self.SearchTagMythicTreeID = SearchTagMythicTreeID
        self.SearchTagSource = SearchTagSource
        self.SearchTagData = SearchTagData
        self.SearchTagURL = SearchTagURL
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "search_tag_id": self.SearchTagID,
            "search_tag_task_id": self.SearchTagTaskID,
            "search_tag_file_id": self.SearchTagFileID,
            "search_tag_credential_id": self.SearchTagCredentialID,
            "search_tag_mythictree_id": self.SearchTagMythicTreeID,
            "search_tag_source": self.SearchTagSource,
            "search_tag_data": self.SearchTagData,
            "search_tag_url": self.SearchTagURL
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


class MythicRPCTagSearchMessageResponse:
    Tags: list[MythicRPCTagData]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 tags: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Tags = [MythicRPCTagData(**x) for x in tags] if tags is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCTagSearch(
        msg: MythicRPCTagSearchMessage) -> MythicRPCTagSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TAG_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCTagSearchMessageResponse(**response)