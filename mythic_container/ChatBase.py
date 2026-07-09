from collections.abc import Awaitable, Callable
from typing import Any

import asyncio
import uuid
import json
import mythic_container
from .SharedClasses import ContainerOnStartMessage, ContainerOnStartMessageResponse


CHAT_INPUT_REQUESTED_SPECIAL_TYPE = "input_requested"
CHAT_TOOL_USE_SPECIAL_TYPE = "tool_use"
CHAT_SUBAGENT_SPECIAL_TYPE = "subagent"


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


class ChatSlashCommandInvocation:
    def __init__(
            self,
            name: str = "",
            argument: str = "",
            raw: str = "",
            source: str = "",
            **kwargs):
        self.Name = name
        self.Argument = argument
        self.Raw = raw
        self.Source = source

    def to_json(self):
        return {
            "name": self.Name,
            "argument": self.Argument,
            "raw": self.Raw,
            "source": self.Source,
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
            model: str = "",
            prompt: str = "",
            config: dict = None,
            context: list[dict] = None,
            secrets: dict = None,
            slash_command: dict = None,
            input_response: dict = None,
            delegation_id: str = "",
            delegation_name: str = "",
            **kwargs):
        self.ContainerName = container_name
        self.OperationID = operation_id
        self.ChannelID = channel_id
        self.APITokenID = apitokens_id
        self.ChannelName = channel_name
        self.ChannelSlug = channel_slug
        self.RequestID = request_id
        self.RequestMessageID = request_message_id
        self.Model = model
        self.Prompt = prompt
        self.Config = config if config is not None else {}
        self.Context = [ChatMessageContext(**x) for x in context] if context is not None else []
        self.Secrets = secrets if secrets is not None else {}
        self.SlashCommand = ChatSlashCommandInvocation(**slash_command) if isinstance(slash_command, dict) else None
        self.InputResponse = ChatInputResponse(**input_response) if isinstance(input_response, dict) else None
        self.DelegationID = delegation_id
        self.DelegationName = delegation_name

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
            "model": self.Model,
            "prompt": self.Prompt,
            "config": self.Config,
            "context": [x.to_json() for x in self.Context],
            "secrets": self.Secrets,
            "slash_command": self.SlashCommand.to_json() if self.SlashCommand is not None else None,
            "input_response": self.InputResponse.to_json() if self.InputResponse is not None else None,
            "delegation_id": self.DelegationID,
            "delegation_name": self.DelegationName,
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
            reason: str = "",
            cancelled_by: int = 0,
            **kwargs):
        self.ContainerName = container_name
        self.OperationID = operation_id
        self.ChannelID = channel_id
        self.RequestID = request_id
        self.Reason = reason
        self.CancelledBy = cancelled_by

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "operation_id": self.OperationID,
            "channel_id": self.ChannelID,
            "request_id": self.RequestID,
            "reason": self.Reason,
            "cancelled_by": self.CancelledBy,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ChatInputChoice:
    def __init__(
            self,
            id: str = "",
            label: str = "",
            description: str = "",
            data: dict = None,
            **kwargs):
        self.ID = id
        self.Label = label
        self.Description = description
        self.Data = data if data is not None else {}
        self.AdditionalItems = dict(kwargs)

    def to_json(self):
        result = {
            "id": self.ID,
            "label": self.Label,
            "description": self.Description,
            "data": self.Data,
        }
        result.update(_to_json_value(self.AdditionalItems))
        return result


class ChatInputResponse:
    def __init__(
            self,
            action: str = "",
            response: str = "",
            choice: dict = None,
            input_request_message_id: int = 0,
            input_request: dict = None,
            resolved_by_operator_id: int = 0,
            resolved_by: str = "",
            resolved_at: str = "",
            **kwargs):
        self.Action = action
        self.Response = response
        self.Choice = choice if choice is not None else {}
        self.InputRequestMessageID = input_request_message_id
        self.InputRequest = input_request if input_request is not None else {}
        self.ResolvedByOperatorID = resolved_by_operator_id
        self.ResolvedBy = resolved_by
        self.ResolvedAt = resolved_at
        self.AdditionalItems = dict(kwargs)

    def to_json(self):
        result = {
            "action": self.Action,
            "response": self.Response,
            "choice": self.Choice,
            "input_request_message_id": self.InputRequestMessageID,
            "input_request": self.InputRequest,
            "resolved_by_operator_id": self.ResolvedByOperatorID,
            "resolved_by": self.ResolvedBy,
            "resolved_at": self.ResolvedAt,
        }
        result.update(_to_json_value(self.AdditionalItems))
        return result


class ChatResponse:
    def __init__(
            self,
            OperationID: int = 0,
            RequestID: int = 0,
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


class ChatChannelMetadataUpdate:
    def __init__(
            self,
            OperationID: int = 0,
            ChannelID: int = 0,
            ContainerName: str = "",
            ChannelMetadata: dict[str, Any] | None = None,
            **kwargs):
        self.OperationID = OperationID
        self.ChannelID = ChannelID
        self.ContainerName = ContainerName
        self.ChannelMetadata = ChannelMetadata if ChannelMetadata is not None else {}

    def to_json(self):
        return {
            "operation_id": self.OperationID,
            "channel_id": self.ChannelID,
            "container_name": self.ContainerName,
            "channel_metadata": _to_json_value(self.ChannelMetadata),
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ChatChannelMetadataUpdateResponse:
    def __init__(
            self,
            success: bool = False,
            error: str = "",
            **kwargs):
        self.Success = success
        self.Error = error


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


class ChatSlashCommandDefinition:
    """A slash command a chat model can handle directly.

    Attributes:
        Name (str): Command name without the leading slash.
        Description (str): Short description shown in Mythic command pickers.
    """

    def __init__(
            self,
            Name: str = "",
            Description: str = "",
            **kwargs):
        self.Name = Name
        self.Description = Description
        self.AdditionalItems = {}
        for k, v in kwargs.items():
            self.AdditionalItems[k] = v

    def to_json(self):
        r = {
            "name": self.Name,
            "description": self.Description,
        }
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
        JSONStringSchema (dict): Mythic-style structured JSON editor schema for json config editors.
        Examples (list[dict]): Optional examples operators can load into json config editors.
        HelpText (str): Longer operator-facing help for complex config fields.
        MinRows (int): Preferred minimum visible rows for multiline/json config editors.
        DisplayAsChip (bool): True to show this scalar value as a compact chip in the Mythic chat UI.
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
            JSONStringSchema: dict = None,
            Examples: list[dict] = None,
            HelpText: str = "",
            MinRows: int = 0,
            DisplayAsChip: bool = False,
            **kwargs):
        self.Name = Name
        self.DisplayName = DisplayName
        self.Type = Type
        self.Description = Description
        self.Required = Required
        self.DefaultValue = DefaultValue
        self.Choices = Choices if Choices is not None else []
        self.JSONSchema = JSONSchema
        self.JSONStringSchema = JSONStringSchema
        self.Examples = Examples if Examples is not None else []
        self.HelpText = HelpText
        self.MinRows = MinRows
        self.DisplayAsChip = DisplayAsChip
        self.AdditionalItems = {}
        if self.JSONStringSchema is None and "json_string_schema" in kwargs:
            self.JSONStringSchema = kwargs.pop("json_string_schema")
        if "display_as_chip" in kwargs:
            self.DisplayAsChip = kwargs.pop("display_as_chip")
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
        if self.JSONStringSchema is not None:
            r["json_string_schema"] = _to_json_value(self.JSONStringSchema)
        if self.Examples:
            r["examples"] = _to_json_value(self.Examples)
        if self.HelpText:
            r["help_text"] = self.HelpText
        if self.MinRows:
            r["min_rows"] = self.MinRows
        if self.DisplayAsChip:
            r["display_as_chip"] = self.DisplayAsChip
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
        SlashCommands (list[ChatSlashCommandDefinition]): Slash commands this model can handle directly.
    """

    def __init__(
            self,
            Provider: str = "",
            ConfigurationOptions: list[ChatModelConfigurationOption] = None,
            RequiredUserSecrets: list[str] = None,
            OptionalUserSecrets: list[str] = None,
            RequiredChannelAPITokenScopes: list[str] = None,
            SlashCommands: list[ChatSlashCommandDefinition] = None,
            **kwargs):
        self.Provider = Provider
        self.ConfigurationOptions = ConfigurationOptions if ConfigurationOptions is not None else []
        self.RequiredUserSecrets = RequiredUserSecrets if RequiredUserSecrets is not None else []
        self.OptionalUserSecrets = OptionalUserSecrets if OptionalUserSecrets is not None else []
        self.RequiredChannelAPITokenScopes = (
            RequiredChannelAPITokenScopes if RequiredChannelAPITokenScopes is not None else []
        )
        self.SlashCommands = SlashCommands if SlashCommands is not None else []
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
            "slash_commands": [_to_json_value(x) for x in self.SlashCommands],
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


class ChatValueReader:
    """Typed reader for chat config and secret dictionaries.

    Subclasses should still define a typed dataclass for their settings. This
    reader keeps that dataclass loader explicit and readable without requiring
    repetitive dictionary coercion in every chat container.
    """

    def __init__(self, values: dict[str, Any] | None, label: str = "chat values"):
        self.values = values if isinstance(values, dict) else {}
        self.label = label

    def has(self, key: str) -> bool:
        return key in self.values

    def raw(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def text(self, key: str, default: str = "") -> str:
        value = self._scalar_to_text(self.raw(key))
        return value if value else default

    def required_text(self, key: str) -> str:
        value = self.text(key)
        if not value:
            raise RuntimeError(f"{key} is required in {self.label}.")
        return value

    def integer(self, key: str, default: int = 0) -> int:
        value = self.text(key)
        if not value:
            return default
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{key} must be an integer in {self.label}.") from exc

    def boolean(self, key: str, default: bool = False) -> bool:
        value = self.text(key).lower()
        if not value:
            return default
        if value in {"1", "true", "yes", "y", "on"}:
            return True
        if value in {"0", "false", "no", "n", "off"}:
            return False
        raise ValueError(f"{key} must be a boolean value in {self.label}.")

    def dict_value(self, key: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
        value = self.raw(key)
        if isinstance(value, dict):
            return value
        return dict(default or {})

    def list_value(self, key: str, default: list[Any] | None = None) -> list[Any]:
        value = self.raw(key)
        if isinstance(value, list):
            return value
        return list(default or [])

    def _scalar_to_text(self, value: Any) -> str:
        if value is None or isinstance(value, (dict, list)):
            return ""
        return str(value).strip()


class ChatConfigView(ChatValueReader):
    @classmethod
    def from_request(cls, request: ChatRequest):
        return cls(getattr(request, "Config", None), "chat model configuration")


class ChatSecretView(ChatValueReader):
    @classmethod
    def from_request(cls, request: ChatRequest):
        return cls(getattr(request, "Secrets", None), "Mythic user secrets")

    def _scalar_to_text(self, value: Any) -> str:
        if isinstance(value, dict):
            for candidate_key in ("value", "Value", "secret", "Secret"):
                if candidate_key in value:
                    value = value[candidate_key]
                    break
        return super()._scalar_to_text(value)


class ChatAPITokenProvider:
    """Creates and caches Mythic API tokens scoped to an AI chat channel."""

    _cache: dict[tuple[int, int, int], "ChatAPITokenProvider"] = {}
    _cache_lock = asyncio.Lock()

    def __init__(
            self,
            operation_id: int,
            chat_channel_id: int,
            backing_apitoken_id: int = 0):
        self.operation_id = operation_id
        self.chat_channel_id = chat_channel_id
        self.backing_apitoken_id = backing_apitoken_id
        self._api_token = ""
        self._token_lock = asyncio.Lock()

    @classmethod
    async def create(cls, operation_id: int, chat_channel_id: int, backing_apitoken_id: int = 0):
        cache_key = (operation_id, chat_channel_id, backing_apitoken_id)
        async with cls._cache_lock:
            cached_provider = cls._cache.get(cache_key)
            if cached_provider is not None:
                return cached_provider
            for existing_key in list(cls._cache):
                existing_operation_id, existing_channel_id, _ = existing_key
                if existing_operation_id == operation_id and existing_channel_id == chat_channel_id:
                    cls._cache.pop(existing_key, None)
            instance = cls(operation_id, chat_channel_id, backing_apitoken_id)
            cls._cache[cache_key] = instance
            return instance

    @classmethod
    async def from_request(cls, request: ChatRequest):
        return await cls.create(
            request.OperationID,
            request.ChannelID,
            getattr(request, "APITokenID", 0),
        )

    async def get_token(self) -> str:
        if self._api_token:
            return self._api_token
        async with self._token_lock:
            if self._api_token:
                return self._api_token
            from mythic_container.MythicGoRPC import SendMythicRPCAPITokenCreate, MythicRPCAPITokenCreateMessage
            resp = await SendMythicRPCAPITokenCreate(
                MythicRPCAPITokenCreateMessage(ChatChannelID=self.chat_channel_id)
            )
            if not resp.Success:
                raise RuntimeError(f"failed to create chat-channel Mythic API token: {resp.Error}")
            self._api_token = resp.APIToken
            return self._api_token


class ChatTurnContext:
    """Small convenience wrapper for a single Mythic chat request.

    Chat subclasses can pass this object into their provider-specific code so
    that code can stream one visible output block without re-supplying its
    response_key for every delta. response_key is the Mythic UI block to update;
    it is not a provider request ID, auth token, or model-specific identifier.
    """

    def __init__(
            self,
            chat: "Chat",
            request: ChatRequest,
            response_key: str,
            model: str = "",
            metadata: dict[str, Any] | None = None):
        self.chat = chat
        self.request = request
        self.response_key = chat.require_response_key(response_key)
        self.model = model or request.Model
        self.metadata = metadata if metadata is not None else {}

    async def send_streaming(self, content: str = "", metadata: dict[str, Any] | None = None):
        await self.chat.send_streaming(self.request, self.response_key, content=content, metadata=self._metadata(metadata))

    async def send_delta(self, content: str, metadata: dict[str, Any] | None = None):
        await self.chat.send_delta(self.request, self.response_key, content=content, metadata=self._metadata(metadata))

    async def send_text(self, content: str, metadata: dict[str, Any] | None = None):
        await self.chat.send_text(self.request, self.response_key, content=content, metadata=self._metadata(metadata))

    async def send_complete(
            self,
            metadata: dict[str, Any] | None = None,
            content: str = "",
            complete_request: bool = False):
        await self.chat.send_complete(
            self.request,
            self.response_key,
            metadata=self._metadata(metadata),
            content=content,
            complete_request=complete_request,
        )

    async def send_error(self, error: str, metadata: dict[str, Any] | None = None, complete_request: bool = True):
        await self.chat.send_error(
            self.request,
            self.response_key,
            error=error,
            metadata=self._metadata(metadata),
            complete_request=complete_request,
        )

    async def send_input_request(
            self,
            input_request: Any,
            metadata: dict[str, Any] | None = None,
            response_key: str = ""):
        await self.chat.send_input_request(self.request, input_request, metadata=self._metadata(metadata), response_key=response_key)

    async def send_approval_request(
            self,
            title: str,
            prompt: str,
            description: str = "",
            data: dict[str, Any] | None = None,
            metadata: dict[str, Any] | None = None,
            response_key: str = ""):
        await self.chat.send_approval_request(
            self.request,
            title=title,
            prompt=prompt,
            description=description,
            data=data,
            metadata=self._metadata(metadata),
            response_key=response_key,
        )

    async def send_single_choice_request(
            self,
            title: str,
            prompt: str,
            choices: list[Any],
            description: str = "",
            data: dict[str, Any] | None = None,
            metadata: dict[str, Any] | None = None,
            response_key: str = ""):
        await self.chat.send_single_choice_request(
            self.request,
            title=title,
            prompt=prompt,
            choices=choices,
            description=description,
            data=data,
            metadata=self._metadata(metadata),
            response_key=response_key,
        )

    async def send_subagent_status(
            self,
            title: str,
            prompt: str = "",
            delegation_id: str = "",
            delegation_name: str = "",
            status: str = "running",
            tool_count: int | None = None,
            tool_total: int | None = None,
            icon: str = "",
            icon_color: str = "",
            content: str = "",
            response_key: str = "",
            complete: bool = False,
            complete_request: bool = False,
            metadata: dict[str, Any] | None = None):
        """Send or update a flat sub-agent delegation summary card.

        Use one stable ``delegation_id`` for the sub-agent card, delegated tool
        cards, delegated input requests, side-pane operator prompts, and the
        final delegated response. Mythic shows the summary card in the main
        chat, filters the drill-down pane by ``delegation_id``, and keeps
        delegated approvals visible in the main chat while pending.
        """
        await self.chat.send_subagent_status(
            self.request,
            title=title,
            prompt=prompt,
            delegation_id=delegation_id,
            delegation_name=delegation_name,
            status=status,
            tool_count=tool_count,
            tool_total=tool_total,
            icon=icon,
            icon_color=icon_color,
            content=content,
            response_key=response_key,
            complete=complete,
            complete_request=complete_request,
            metadata=self._metadata(metadata),
        )

    async def update_channel_metadata(self, channel_metadata: dict[str, Any]) -> ChatChannelMetadataUpdateResponse:
        return await self.chat.update_channel_metadata(self.request, channel_metadata)

    def _metadata(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        """Merge turn metadata and propagate delegated side-pane metadata."""
        merged = dict(self.metadata)
        if extra:
            merged.update(extra)
        if self.request.DelegationID and "delegation_id" not in merged:
            merged["delegation_id"] = self.request.DelegationID
        if self.request.DelegationName and "delegation_name" not in merged:
            merged["delegation_name"] = self.request.DelegationName
        return merged


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

    def turn_context(
            self,
            request: ChatRequest,
            response_key: str,
            model: str = "",
            metadata: dict[str, Any] | None = None) -> ChatTurnContext:
        return ChatTurnContext(self, request, response_key=response_key, model=model, metadata=metadata)

    async def run_chat_turn(
            self,
            request: ChatRequest,
            handler: Callable[[ChatTurnContext], Awaitable[Any]],
            response_key: str = "",
            model: str = "",
            metadata: dict[str, Any] | None = None,
            complete_metadata: dict[str, Any] | None = None,
            complete_content: str = "",
            complete_request: bool = True,
            error_formatter: Callable[[Exception], str] | None = None) -> Any:
        """Run the common Mythic chat response lifecycle around custom logic.

        This is intentionally provider-neutral. The subclass still owns how it
        reads settings, connects to an LLM, invokes tools, and streams deltas.
        response_key is required because Mythic creates and updates visible
        response parts lazily. Reuse the same key for all deltas in one text
        block; use a different key for tool cards or later assistant text.
        """

        response_key = self.require_response_key(response_key)
        turn = self.turn_context(request, response_key=response_key, model=model, metadata=metadata)
        try:
            result = await handler(turn)
        except asyncio.CancelledError:
            raise
        except Exception as error:
            message = error_formatter(error) if error_formatter is not None else str(error)
            await turn.send_error(message)
            return None

        if result is None:
            return None

        merged_metadata = dict(complete_metadata or {})
        if isinstance(result, dict):
            merged_metadata.update(result)
        await self.send_complete(
            request,
            response_key,
            metadata=turn._metadata(merged_metadata),
            content=complete_content,
            complete_request=complete_request,
        )
        return result

    def require_response_key(self, response_key: str) -> str:
        response_key = str(response_key or "").strip()
        if not response_key:
            raise ValueError("response_key is required for chat responses")
        return response_key

    async def send_response(
            self,
            request: ChatRequest,
            response_key: str,
            content: str = "",
            is_delta: bool = False,
            complete: bool = False,
            complete_request: bool = False,
            status: str = "",
            error: str = "",
            metadata: dict[str, Any] | None = None) -> None:
        response_key = self.require_response_key(response_key)
        await SendMythicRPCChatResponse(ChatResponse(
            OperationID=request.OperationID,
            RequestID=request.RequestID,
            ResponseKey=response_key,
            Content=content,
            IsDelta=is_delta,
            Complete=complete,
            CompleteRequest=complete_request,
            Status=status,
            Error=error,
            Metadata=metadata if metadata is not None else {},
        ))

    async def update_channel_metadata(
            self,
            request: ChatRequest,
            channel_metadata: dict[str, Any]) -> ChatChannelMetadataUpdateResponse:
        return await SendMythicRPCChatChannelMetadataUpdate(ChatChannelMetadataUpdate(
            OperationID=request.OperationID,
            ChannelID=request.ChannelID,
            ContainerName=self.name or request.ContainerName,
            ChannelMetadata=channel_metadata,
        ))

    async def send_streaming(
            self,
            request: ChatRequest,
            response_key: str,
            content: str = "",
            metadata: dict[str, Any] | None = None) -> None:
        await self.send_response(request, response_key, content=content, status="streaming", metadata=metadata)

    async def send_delta(
            self,
            request: ChatRequest,
            response_key: str,
            content: str,
            metadata: dict[str, Any] | None = None) -> None:
        await self.send_response(request, response_key, content=content, is_delta=True, status="streaming", metadata=metadata)

    async def send_text(
            self,
            request: ChatRequest,
            response_key: str,
            content: str,
            metadata: dict[str, Any] | None = None) -> None:
        await self.send_response(request, response_key, content=content, status="streaming", metadata=metadata)

    async def send_complete(
            self,
            request: ChatRequest,
            response_key: str,
            metadata: dict[str, Any] | None = None,
            content: str = "",
            complete_request: bool = False) -> None:
        await self.send_response(
            request,
            response_key,
            content=content,
            complete=True,
            complete_request=complete_request,
            status="complete",
            metadata=metadata,
        )

    async def send_error(
            self,
            request: ChatRequest,
            response_key: str,
            error: str,
            metadata: dict[str, Any] | None = None,
            complete_request: bool = True) -> None:
        await self.send_response(
            request,
            response_key,
            status="error",
            error=error,
            complete=True,
            complete_request=complete_request,
            metadata=metadata,
        )

    async def send_input_request(
            self,
            request: ChatRequest,
            input_request: Any,
            metadata: dict[str, Any] | None = None,
            response_key: str = "") -> None:
        input_request_metadata = self.normalize_input_request(input_request)
        response_key = self.require_response_key(response_key) if response_key else f"input_requested:{uuid.uuid4()}"
        prompt = input_request_metadata.get("prompt") or input_request_metadata.get("description") or "Input is required before continuing."
        await self.send_complete(
            request,
            response_key,
            content=prompt,
            complete_request=False,
            metadata={
                **(metadata or {}),
                "special_type": CHAT_INPUT_REQUESTED_SPECIAL_TYPE,
                "input_requested": input_request_metadata,
            },
        )

    async def send_approval_request(
            self,
            request: ChatRequest,
            title: str,
            prompt: str,
            description: str = "",
            data: dict[str, Any] | None = None,
            metadata: dict[str, Any] | None = None,
            response_key: str = "") -> None:
        await self.send_input_request(request, {
            "status": "pending",
            "input_type": "approval",
            "title": title,
            "prompt": prompt,
            "description": description,
            "data": data or {},
        }, metadata=metadata, response_key=response_key)

    async def send_single_choice_request(
            self,
            request: ChatRequest,
            title: str,
            prompt: str,
            choices: list[Any],
            description: str = "",
            data: dict[str, Any] | None = None,
            metadata: dict[str, Any] | None = None,
            response_key: str = "") -> None:
        await self.send_input_request(request, {
            "status": "pending",
            "input_type": "single_choice",
            "title": title,
            "prompt": prompt,
            "description": description,
            "choices": [_to_json_value(choice) for choice in choices],
            "data": data or {},
        }, metadata=metadata, response_key=response_key)

    async def send_subagent_status(
            self,
            request: ChatRequest,
            title: str,
            prompt: str = "",
            delegation_id: str = "",
            delegation_name: str = "",
            status: str = "running",
            tool_count: int | None = None,
            tool_total: int | None = None,
            icon: str = "",
            icon_color: str = "",
            content: str = "",
            response_key: str = "",
            complete: bool = False,
            complete_request: bool = False,
            metadata: dict[str, Any] | None = None) -> None:
        """Send or update a sub-agent summary card.

        ``delegation_id`` is the flat grouping key. Mythic does not nest cards;
        it renders the sub-agent card in the main chat and opens a drill-down
        pane by filtering channel messages with this id. ``icon`` and
        ``icon_color`` are optional developer-provided visuals; the UI derives
        deterministic fallbacks when they are omitted.
        """
        delegation_id = delegation_id or request.DelegationID
        delegation_name = delegation_name or request.DelegationName
        subagent = {
            "title": title,
            "status": status,
        }
        if prompt:
            subagent["prompt"] = prompt
        if tool_count is not None:
            subagent["tool_count"] = tool_count
        if tool_total is not None:
            subagent["tool_total"] = tool_total
        if icon:
            subagent["icon"] = icon
        if icon_color:
            subagent["icon_color"] = icon_color
        response_metadata = dict(metadata or {})
        response_metadata["special_type"] = CHAT_SUBAGENT_SPECIAL_TYPE
        response_metadata["subagent"] = subagent
        if delegation_id:
            response_metadata["delegation_id"] = delegation_id
        if delegation_name:
            response_metadata["delegation_name"] = delegation_name
        response_key = response_key or f"subagent:{self._response_key_fragment(delegation_id or title)}"
        await self.send_response(
            request,
            response_key=response_key,
            content=content,
            status="complete" if complete else "streaming",
            complete=complete,
            complete_request=complete_request,
            metadata=response_metadata,
        )

    def normalize_input_request(self, input_request: Any) -> dict[str, Any]:
        if hasattr(input_request, "to_input_request") and callable(input_request.to_input_request):
            normalized = input_request.to_input_request()
        elif hasattr(input_request, "to_json") and callable(input_request.to_json):
            normalized = input_request.to_json()
        else:
            normalized = input_request
        if not isinstance(normalized, dict):
            normalized = {}
        normalized = dict(_to_json_value(normalized))
        normalized.setdefault("status", "pending")
        normalized.setdefault("input_type", "approval")
        normalized.setdefault("title", "Input requested")
        normalized.setdefault("prompt", normalized.get("description", "Input is required before continuing."))
        normalized.setdefault("data", {})
        if normalized.get("input_type") == "single_choice":
            normalized["choices"] = [_to_json_value(choice) for choice in normalized.get("choices", [])]
        return normalized

    def _response_key_fragment(self, value: str) -> str:
        fragment = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(value).strip().lower())
        return fragment.strip("_")[:80] or "input"

    def build_chat_messages(
            self,
            request: ChatRequest,
            system_prompt: str = "",
            max_context_messages: int = 0,
            include_sender_names: bool = True,
            current_sender_default: str = "operator") -> list[dict[str, str]]:
        context = (
            request.Context[-max_context_messages:]
            if max_context_messages > 0
            else request.Context
        )
        current_sender = current_sender_default
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for context_message in context:
            if context_message.ID == request.RequestMessageID:
                current_sender = context_message.SenderDisplayName or current_sender
                continue
            role = "assistant" if context_message.AuthorType == "ai" else "user"
            sender = context_message.SenderDisplayName or context_message.AuthorType or current_sender_default
            content = context_message.Message
            if include_sender_names and role == "user":
                content = f"{sender}: {content}"
            messages.append({"role": role, "content": content})
        prompt = request.Prompt
        if include_sender_names:
            prompt = f"{current_sender}: {prompt}"
        messages.append({"role": "user", "content": prompt})
        return messages

    def normalize_stream_delta(self, delta: Any) -> str:
        if delta is None:
            return ""
        if isinstance(delta, str):
            return delta
        if isinstance(delta, list):
            return "".join(self.normalize_stream_delta(part) for part in delta)
        if isinstance(delta, dict):
            for key in ("text", "content"):
                value = delta.get(key)
                if isinstance(value, str):
                    return value
                if isinstance(value, (dict, list)):
                    normalized = self.normalize_stream_delta(value)
                    if normalized:
                        return normalized
        for attr in ("text", "content"):
            value = getattr(delta, attr, None)
            if isinstance(value, str):
                return value
            if isinstance(value, (dict, list)):
                normalized = self.normalize_stream_delta(value)
                if normalized:
                    return normalized
        return ""

    def truncate_text(self, text: str, max_chars: int) -> str:
        if max_chars <= 0 or len(text) <= max_chars:
            return text
        return text[:max_chars] + f"\n\n[truncated to {max_chars} characters]"

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


async def SendMythicRPCChatChannelMetadataUpdate(
        update: ChatChannelMetadataUpdate) -> ChatChannelMetadataUpdateResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
        queue=mythic_container.CHAT_CHANNEL_METADATA_UPDATE_ROUTING_KEY,
        body=update.to_json(),
    )
    return ChatChannelMetadataUpdateResponse(**response)


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
