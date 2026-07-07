# Chat Containers

The `Chat` base class gives chat containers a small Mythic lifecycle and a set
of optional helpers. It does not decide how your model provider, API keys, HTTP
headers, or MCP server configuration should work. Keep those semantics in your
own container and map your typed settings into the reusable helpers.

## Subclassing Chat

Every chat container defines metadata and one async `chat` entrypoint:

```python
from dataclasses import dataclass

from mythic_container.ChatBase import (
    Chat,
    ChatConfigView,
    ChatModelDefinition,
    ChatModelMetadata,
    ChatRequest,
    ChatSecretView,
)


@dataclass(frozen=True)
class MyProviderSettings:
    api_key: str
    base_url: str
    model: str
    max_context_messages: int

    @classmethod
    def from_request(cls, msg: ChatRequest):
        config = ChatConfigView.from_request(msg)
        secrets = ChatSecretView.from_request(msg)
        return cls(
            api_key=secrets.required_text("MY_PROVIDER_API_KEY"),
            base_url=config.required_text("MY_PROVIDER_URL"),
            model=config.text("MY_PROVIDER_MODEL", "default-model"),
            max_context_messages=config.integer("MY_MAX_CONTEXT_MESSAGES", 20),
        )


class MyChat(Chat):
    name = "my_chat"
    description = "Example provider-backed chat container."
    semver = "0.1.0"
    models = [
        ChatModelDefinition(
            Name="My Provider",
            Description="Streams responses from my provider.",
            Metadata=ChatModelMetadata(Provider="my-provider"),
        ),
    ]

    async def chat(self, msg: ChatRequest) -> None:
        settings = MyProviderSettings.from_request(msg)
        metadata = {"model": msg.Model, "provider_model": settings.model}
        response_key = f"assistant:my-provider:{msg.RequestID}"
        await self.send_streaming(msg, response_key, metadata=metadata)

        messages = self.build_chat_messages(
            msg,
            system_prompt="You are an assistant embedded in Mythic.",
            max_context_messages=settings.max_context_messages,
        )

        async for delta in stream_from_my_provider(settings, messages):
            await self.send_delta(msg, response_key, delta, metadata=metadata)

        await self.send_complete(msg, response_key, metadata=metadata, complete_request=True)
```

The important pattern is that `MyProviderSettings` owns the config contract. The
base class only helps read typed values from `msg.Config` and `msg.Secrets`.

## Response Helpers

Use response helpers when you want Mythic-compatible status messages without
constructing `ChatResponse` objects by hand:

```python
response_key = f"assistant:my-provider:{msg.RequestID}"
await self.send_streaming(msg, response_key, metadata={"provider": "my-provider"})
await self.send_delta(msg, response_key, "partial text", metadata={"provider": "my-provider"})
await self.send_text(msg, "status:my-provider", "non-delta status text")
await self.send_complete(msg, response_key, metadata={"response_id": "abc"}, complete_request=True)
await self.send_error(msg, "assistant:error", "provider request failed")
```

`response_key` names the visible output block Mythic should create or update.
Use one stable key for all deltas in a streamed answer, and a different stable
key for tool-use cards, MCP confirmations, or other interleaved output.

`build_chat_messages(...)` converts Mythic chat context into provider-friendly
role/content messages. Override your own method or call it with different
arguments if your provider needs a different format.

## MCP Primitives

MCP support is intentionally typed and connection-agnostic. The core library
does not parse a universal `MCP_SERVERS` config object. Your container maps its
own settings into connection objects:

```python
from mythic_container.chat_mcp import (
    MCPStreamableHTTPConnection,
    MCPToolClient,
)


async def load_mcp_tools(msg, settings):
    connection = MCPStreamableHTTPConnection(
        name="docs",
        url=settings.docs_mcp_url,
        headers={"Authorization": f"Bearer {settings.docs_mcp_token}"},
        read_only_tools=("search_docs",),
    )
    return await MCPToolClient.create(connections=[connection])
```

For local tools:

```python
from mythic_container.chat_mcp import MCPStdioConnection

connection = MCPStdioConnection(
    name="local",
    command="python3",
    args=("-m", "my_mcp_server"),
    env={"MY_TOKEN": settings.local_mcp_token},
    read_only_tools=("list_items",),
)
```

The `read_only_tools` tuple is an allow-list. Other MCP tools raise
`MCPConfirmationRequired`, which can be turned into Mythic's native confirmation
card:

```python
from mythic_container.chat_mcp import MCPConfirmationRequired

try:
    result = await mcp_client.invoke(tool_name, arguments)
except MCPConfirmationRequired as confirmation:
    await self.send_mcp_confirmation(msg, confirmation, metadata={"provider": "my-provider"})
    return
```

When Mythic sends an approved tool call back in `msg.ConfirmedToolCall`, rebuild
the same typed connections and call `invoke_confirmed(...)`:

```python
tool_call = msg.ConfirmedToolCall
result = await mcp_client.invoke_confirmed(
    tool_call.get("tool_name", ""),
    tool_call.get("arguments", {}),
    server_name=tool_call.get("server_name", ""),
)
```

The `langchain-mcp-adapters` package is imported lazily. Containers that use
MCP should include it in their own requirements.
