from collections.abc import Awaitable, Callable
from typing import Any

import json
import mythic_container
from .SharedClasses import ContainerOnStartMessage, ContainerOnStartMessageResponse


def _to_json_value(value: Any):
    if hasattr(value, "to_json") and callable(value.to_json):
        return value.to_json()
    if isinstance(value, list):
        return [_to_json_value(x) for x in value]
    if isinstance(value, dict):
        return {k: _to_json_value(v) for k, v in value.items()}
    return value


class ChatMessageContext:
    def __init__(
            self,
            id: int = 0,
            author_type: str = "",
            sender_display_name: str = "",
            message: str = "",
            metadata: dict = None,
            created_at: str = "",
            **kwargs):
        self.ID = id
        self.AuthorType = author_type
        self.SenderDisplayName = sender_display_name
        self.Message = message
        self.Metadata = metadata if metadata is not None else {}
        self.CreatedAt = created_at

    def to_json(self):
        return {
            "id": self.ID,
            "author_type": self.AuthorType,
            "sender_display_name": self.SenderDisplayName,
            "message": self.Message,
            "metadata": self.Metadata,
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
            confirmed_tool_call: dict = None,
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
        self.ConfirmedToolCall = confirmed_tool_call if confirmed_tool_call is not None else {}

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
            "confirmed_tool_call": self.ConfirmedToolCall,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ChatCancelRequest:
    def __init__(
            self,
            container_name: str = "",
            operation_id: int = 0,
            channel_id: int = 0,
            request_id: int = 0,
            response_message_id: int = 0,
            reason: str = "",
            cancelled_by: int = 0,
            **kwargs):
        self.ContainerName = container_name
        self.OperationID = operation_id
        self.ChannelID = channel_id
        self.RequestID = request_id
        self.ResponseMessageID = response_message_id
        self.Reason = reason
        self.CancelledBy = cancelled_by

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "operation_id": self.OperationID,
            "channel_id": self.ChannelID,
            "request_id": self.RequestID,
            "response_message_id": self.ResponseMessageID,
            "reason": self.Reason,
            "cancelled_by": self.CancelledBy,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ChatResponse:
    def __init__(
            self,
            OperationID: int = 0,
            RequestID: int = 0,
            ResponseMessageID: int = 0,
            ResponseKey: str = "",
            Content: str = "",
            IsDelta: bool = False,
            Complete: bool = False,
            CompleteRequest: bool = False,
            Status: str = "",
            Error: str = "",
            Metadata: dict = None,
            **kwargs):
        self.OperationID = OperationID
        self.RequestID = RequestID
        self.ResponseMessageID = ResponseMessageID
        self.ResponseKey = ResponseKey
        self.Content = Content
        self.IsDelta = IsDelta
        self.Complete = Complete
        self.CompleteRequest = CompleteRequest
        self.Status = Status
        self.Error = Error
        self.Metadata = Metadata if Metadata is not None else {}

    def to_json(self):
        return {
            "operation_id": self.OperationID,
            "request_id": self.RequestID,
            "response_message_id": self.ResponseMessageID,
            "response_key": self.ResponseKey,
            "content": self.Content,
            "is_delta": self.IsDelta,
            "complete": self.Complete,
            "complete_request": self.CompleteRequest,
            "status": self.Status,
            "error": self.Error,
            "metadata": self.Metadata,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ChatModelConfigurationOptionType:
    """Types available for per-chat model configuration options.

    If you don't want to use a listed value, supply your own with
    ChatModelConfigurationOptionType("my_type").
    """
    String = "string"
    Number = "number"
    Choice = "choice"
    Boolean = "boolean"
    JSON = "json"
    Json = "json"

    def __init__(self, option_type: str):
        self.option_type = option_type

    def __str__(self):
        return self.option_type


class ChatModelConfigurationOptionChoice:
    """A selectable value for a ChatModelConfigurationOption.

    Attributes:
        Label (str): Human-readable option shown in the Mythic UI.
        Value (str): Value written into ChatRequest.Config when selected.
        Description (str): Optional helper text for this choice.
    """

    def __init__(
            self,
            Label: str = "",
            Value: str = "",
            Description: str = "",
            **kwargs):
        self.Label = Label
        self.Value = Value
        self.Description = Description
        self.AdditionalItems = {}
        for k, v in kwargs.items():
            self.AdditionalItems[k] = v

    def to_json(self):
        r = {
            "label": self.Label,
            "value": self.Value,
        }
        if self.Description:
            r["description"] = self.Description
        r.update(_to_json_value(self.AdditionalItems))
        return r


class ChatModelConfigurationOption:
    """A per-chat config value exposed in the Mythic UI and delivered in ChatRequest.Config.

    Attributes:
        Name (str): Config key sent to the chat container.
        DisplayName (str): Human-readable label shown in the UI.
        Type (ChatModelConfigurationOptionType): UI input type such as string, number, choice, boolean, or json.
        Description (str): Helper text explaining what the operator should supply.
        Required (bool): True when a value must be supplied before using the model.
        DefaultValue: Initial value shown for this option. The type should match Type.
        Choices (list[ChatModelConfigurationOptionChoice]): Selectable values for choice options.
        JSONSchema (dict): Optional JSON schema shown beside json config editors.
        Examples (list[dict]): Optional examples operators can load into json config editors.
        HelpText (str): Longer operator-facing help for complex config fields.
        MinRows (int): Preferred minimum visible rows for multiline/json config editors.
    """

    def __init__(
            self,
            Name: str = "",
            DisplayName: str = "",
            Type: ChatModelConfigurationOptionType = ChatModelConfigurationOptionType.String,
            Description: str = "",
            Required: bool = False,
            DefaultValue: Any = None,
            Choices: list[ChatModelConfigurationOptionChoice] = None,
            JSONSchema: dict = None,
            Examples: list[dict] = None,
            HelpText: str = "",
            MinRows: int = 0,
            **kwargs):
        self.Name = Name
        self.DisplayName = DisplayName
        self.Type = Type
        self.Description = Description
        self.Required = Required
        self.DefaultValue = DefaultValue
        self.Choices = Choices if Choices is not None else []
        self.JSONSchema = JSONSchema
        self.Examples = Examples if Examples is not None else []
        self.HelpText = HelpText
        self.MinRows = MinRows
        self.AdditionalItems = {}
        for k, v in kwargs.items():
            self.AdditionalItems[k] = v

    def to_json(self):
        r = {
            "name": self.Name,
            "display_name": self.DisplayName,
            "type": str(self.Type),
            "description": self.Description,
            "required": self.Required,
            "choices": [_to_json_value(x) for x in self.Choices]
        }
        if self.DefaultValue is not None:
            r["default_value"] = _to_json_value(self.DefaultValue)
        if self.JSONSchema is not None:
            r["json_schema"] = _to_json_value(self.JSONSchema)
        if self.Examples:
            r["examples"] = _to_json_value(self.Examples)
        if self.HelpText:
            r["help_text"] = self.HelpText
        if self.MinRows:
            r["min_rows"] = self.MinRows
        r.update(_to_json_value(self.AdditionalItems))
        return r


class ChatModelMetadata:
    """Metadata describing how a chat model is configured and what access it needs.

    Mythic syncs this data with the model definition. The UI can render
    ConfigurationOptions for operators, and developers can use the remaining
    fields to document required secrets, API token scopes, provider defaults,
    and compatibility fallbacks.

    Attributes:
        Provider (str): Backing service or model provider such as litellm, openai, anthropic, or a local engine.
        ConfigurationOptions (list[ChatModelConfigurationOption]): Config fields Mythic can render and send in ChatRequest.Config.
        RequiredUserSecrets (list[str]): Mythic user secret names required before this model can be used.
        OptionalUserSecrets (list[str]): Mythic user secret names this model can use when present.
        RequiredChannelAPITokenScopes (list[str]): API token scopes required on the AI chat channel for tool access.
    """

    def __init__(
            self,
            Provider: str = "",
            ConfigurationOptions: list[ChatModelConfigurationOption] = None,
            RequiredUserSecrets: list[str] = None,
            OptionalUserSecrets: list[str] = None,
            RequiredChannelAPITokenScopes: list[str] = None,
            **kwargs):
        self.Provider = Provider
        self.ConfigurationOptions = ConfigurationOptions if ConfigurationOptions is not None else []
        self.RequiredUserSecrets = RequiredUserSecrets if RequiredUserSecrets is not None else []
        self.OptionalUserSecrets = OptionalUserSecrets if OptionalUserSecrets is not None else []
        self.RequiredChannelAPITokenScopes = (
            RequiredChannelAPITokenScopes if RequiredChannelAPITokenScopes is not None else []
        )
        self.AdditionalItems = {}
        for k, v in kwargs.items():
            self.AdditionalItems[k] = v

    def to_json(self):
        r = {
            "provider": self.Provider,
            "configuration_options": [_to_json_value(x) for x in self.ConfigurationOptions],
            "required_user_secrets": self.RequiredUserSecrets,
            "optional_user_secrets": self.OptionalUserSecrets,
            "required_channel_api_token_scopes": self.RequiredChannelAPITokenScopes,
        }
        r.update(_to_json_value(self.AdditionalItems))
        return r


class ChatModelDefinition:
    """One model exposed by a Chat container.

    Metadata should be a ChatModelMetadata instance describing provider
    configuration, user secrets, per-chat UI config fields, defaults, and any
    API token scopes needed for tool access.
    """

    def __init__(
            self,
            Name: str = "",
            Description: str = "",
            Metadata: ChatModelMetadata = None):
        self.Name = Name
        self.Description = Description
        self.Metadata = Metadata if Metadata is not None else ChatModelMetadata()

    def to_json(self):
        return {
            "name": self.Name,
            "description": self.Description,
            "metadata": _to_json_value(self.Metadata),
        }


class Chat:
    """Chat service definition class for AI-backed operation chat.

    Implement chat to receive a ChatRequest and send one or more ChatResponse
    messages back with SendMythicRPCChatResponse. Mythic cancels the active
    chat coroutine when operators cancel the request.
    """
    name: str = ""
    description: str = ""
    semver: str = ""
    models: list[ChatModelDefinition] = []
    chat: Callable[[ChatRequest], Awaitable[None]] = None

    async def on_container_start(self, message: ContainerOnStartMessage) -> ContainerOnStartMessageResponse:
        return ContainerOnStartMessageResponse(ContainerName=self.name)

    def get_sync_message(self):
        subscriptions = []
        for model in self.models:
            subscriptions.append(json.dumps(model.to_json()))
        return {
            "name": self.name,
            "type": "chat",
            "description": self.description,
            "subscriptions": subscriptions,
            "semver": self.semver,
        }


chatServices: dict[str, Chat] = {}
chatRequestTasks: dict[int, Any] = {}
chatCancelledRequests: set[int] = set()


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
