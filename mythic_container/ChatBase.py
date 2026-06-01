from collections.abc import Awaitable, Callable
from typing import Union

import json
import mythic_container
from .SharedClasses import ContainerOnStartMessage, ContainerOnStartMessageResponse


class ChatMessageContext:
    def __init__(
            self,
            id: int = 0,
            author_type: str = "",
            sender_display_name: str = "",
            message: str = "",
            created_at: str = "",
            **kwargs):
        self.ID = id
        self.AuthorType = author_type
        self.SenderDisplayName = sender_display_name
        self.Message = message
        self.CreatedAt = created_at

    def to_json(self):
        return {
            "id": self.ID,
            "author_type": self.AuthorType,
            "sender_display_name": self.SenderDisplayName,
            "message": self.Message,
            "created_at": self.CreatedAt,
        }


class ChatRequest:
    def __init__(
            self,
            container_name: str = "",
            operation_id: int = 0,
            channel_id: int = 0,
            apitokens_id: int = 0,
            channel_name: str = "",
            channel_slug: str = "",
            request_id: int = 0,
            request_message_id: int = 0,
            response_message_id: int = 0,
            model: str = "",
            prompt: str = "",
            config: dict = None,
            context: list[dict] = None,
            secrets: dict = None,
            **kwargs):
        self.ContainerName = container_name
        self.OperationID = operation_id
        self.ChannelID = channel_id
        self.APITokenID = apitokens_id
        self.ChannelName = channel_name
        self.ChannelSlug = channel_slug
        self.RequestID = request_id
        self.RequestMessageID = request_message_id
        self.ResponseMessageID = response_message_id
        self.Model = model
        self.Prompt = prompt
        self.Config = config if config is not None else {}
        self.Context = [ChatMessageContext(**x) for x in context] if context is not None else []
        self.Secrets = secrets if secrets is not None else {}

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "operation_id": self.OperationID,
            "channel_id": self.ChannelID,
            "apitokens_id": self.APITokenID,
            "channel_name": self.ChannelName,
            "channel_slug": self.ChannelSlug,
            "request_id": self.RequestID,
            "request_message_id": self.RequestMessageID,
            "response_message_id": self.ResponseMessageID,
            "model": self.Model,
            "prompt": self.Prompt,
            "config": self.Config,
            "context": [x.to_json() for x in self.Context],
            "secrets": self.Secrets,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ChatResponse:
    def __init__(
            self,
            OperationID: int = 0,
            RequestID: int = 0,
            ResponseMessageID: int = 0,
            Content: str = "",
            IsDelta: bool = False,
            Complete: bool = False,
            Status: str = "",
            Error: str = "",
            Metadata: dict = None,
            **kwargs):
        self.OperationID = OperationID
        self.RequestID = RequestID
        self.ResponseMessageID = ResponseMessageID
        self.Content = Content
        self.IsDelta = IsDelta
        self.Complete = Complete
        self.Status = Status
        self.Error = Error
        self.Metadata = Metadata if Metadata is not None else {}

    def to_json(self):
        return {
            "operation_id": self.OperationID,
            "request_id": self.RequestID,
            "response_message_id": self.ResponseMessageID,
            "content": self.Content,
            "is_delta": self.IsDelta,
            "complete": self.Complete,
            "status": self.Status,
            "error": self.Error,
            "metadata": self.Metadata,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ChatModelDefinition:
    def __init__(
            self,
            Name: str = "",
            Description: str = "",
            Metadata: dict = None):
        self.Name = Name
        self.Description = Description
        self.Metadata = Metadata if Metadata is not None else {}

    def to_json(self):
        return {
            "name": self.Name,
            "description": self.Description,
            "metadata": self.Metadata,
        }


class Chat:
    """Chat service definition class for AI-backed operation chat.

    Implement chat to receive a ChatRequest and send one or more ChatResponse
    messages back with SendMythicRPCChatResponse.
    """
    name: str = ""
    description: str = ""
    semver: str = ""
    models: list[Union[str, ChatModelDefinition, dict]] = []
    chat: Callable[[ChatRequest], Awaitable[None]] = None

    async def on_container_start(self, message: ContainerOnStartMessage) -> ContainerOnStartMessageResponse:
        return ContainerOnStartMessageResponse(ContainerName=self.name)

    def get_sync_message(self):
        subscriptions = []
        for model in self.models:
            if isinstance(model, ChatModelDefinition):
                subscriptions.append(json.dumps(model.to_json()))
            elif isinstance(model, dict):
                subscriptions.append(json.dumps(model))
            else:
                subscriptions.append(str(model))
        return {
            "name": self.name,
            "type": "chat",
            "description": self.description,
            "subscriptions": subscriptions,
            "semver": self.semver,
        }


chatServices: dict[str, Chat] = {}


async def SendMythicRPCChatResponse(response: ChatResponse) -> None:
    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
        queue=mythic_container.CHAT_RESPONSE_ROUTING_KEY,
        body=response.to_json(),
    )


async def SendMythicRPCSyncChat(chat_name: str) -> bool:
    try:
        chat_services = Chat.__subclasses__()
        for cls in chat_services:
            chat = cls()
            if chat.name == "":
                continue
            if chat.name == chat_name:
                chatServices.pop(chat_name, None)
                chatServices[chat.name] = chat
                await mythic_container.mythic_service.syncChatData(chat)
                return True
        return False
    except Exception:
        return False
