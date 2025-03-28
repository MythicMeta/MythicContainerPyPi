import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_TAGTYPE_GET_OR_CREATE = "mythic_rpc_tagtype_get_or_create"


class MythicRPCTagTypeGetOrCreateMessage:
    def __init__(self,
                 TaskID: int,
                 GetOrCreateTagTypeID: int = None,
                 GetOrCreateTagTypeName: str = None,
                 GetOrCreateTagTypeDescription: str = None,
                 GetOrCreateTagTypeColor: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.GetOrCreateTagTypeID = GetOrCreateTagTypeID
        self.GetOrCreateTagTypeName = GetOrCreateTagTypeName
        self.GetOrCreateTagTypeDescription = GetOrCreateTagTypeDescription
        self.GetOrCreateTagTypeColor = GetOrCreateTagTypeColor
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "get_or_create_tag_type_id": self.GetOrCreateTagTypeID,
            "get_or_create_tag_type_name": self.GetOrCreateTagTypeName,
            "get_or_create_tag_type_description": self.GetOrCreateTagTypeDescription,
            "get_or_create_tag_type_color": self.GetOrCreateTagTypeColor
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


class MythicRPCTagTypeGetOrCreateMessageResponse:
    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 tagtype: dict = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.TagType = MythicRPCTagTypeData(**tagtype) if tagtype is not None else None
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCTagTypeGetOrCreate(
        msg: MythicRPCTagTypeGetOrCreateMessage) -> MythicRPCTagTypeGetOrCreateMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TAGTYPE_GET_OR_CREATE,
                                                                            body=msg.to_json())
    return MythicRPCTagTypeGetOrCreateMessageResponse(**response)