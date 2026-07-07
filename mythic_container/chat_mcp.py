import json
import re
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from mythic_container.logging import logger


MCP_LIST_TOOL_NAME = "mcp_list_available_tools"
MCP_CONFIRMATION_SPECIAL_TYPE = "mcp_tool_confirmation"


class MCPConfirmationRequired(Exception):
    """Raised when an MCP tool needs Mythic-native operator approval."""

    def __init__(self, adapter: "MCPToolAdapter", arguments: dict[str, Any]):
        self.adapter = adapter
        self.arguments = arguments if isinstance(arguments, dict) else {}
        super().__init__(f"MCP tool {adapter.exposed_name} requires operator confirmation")

    def to_metadata(self) -> dict[str, Any]:
        return self.adapter.confirmation_metadata(self.arguments)


class MCPConnectionError(RuntimeError):
    """Raised when a configured MCP server cannot be reached or initialized."""


@dataclass(frozen=True)
class MCPConnection:
    """Base typed MCP connection.

    Subclasses decide how to map developer-owned settings into the shape used by
    langchain-mcp-adapters. Chat containers should build these objects from
    their own explicit config loaders rather than relying on a core dictionary
    schema.
    """

    name: str
    read_only_tools: tuple[str, ...] = ()
    session_kwargs: dict[str, Any] | None = None

    @property
    def transport(self) -> str:
        raise NotImplementedError("MCPConnection subclasses must define transport")

    def to_langchain_connection(self) -> dict[str, Any]:
        raise NotImplementedError("MCPConnection subclasses must implement to_langchain_connection")


@dataclass(frozen=True)
class MCPStdioConnection(MCPConnection):
    command: str = ""
    args: tuple[str, ...] = ()
    env: dict[str, Any] = field(default_factory=dict)
    cwd: str | None = None
    encoding: str = "utf-8"
    encoding_error_handler: str = "strict"

    @property
    def transport(self) -> str:
        return "stdio"

    def to_langchain_connection(self) -> dict[str, Any]:
        if not self.name.strip():
            raise ValueError("MCP stdio connection requires name")
        if not self.command.strip():
            raise ValueError(f"MCP stdio connection {self.name} requires command")
        return {
            "transport": "stdio",
            "command": self.command,
            "args": list(self.args),
            "env": dict(self.env),
            "cwd": self.cwd,
            "encoding": self.encoding,
            "encoding_error_handler": self.encoding_error_handler,
            "session_kwargs": self.session_kwargs,
        }


@dataclass(frozen=True)
class MCPStreamableHTTPConnection(MCPConnection):
    url: str = ""
    headers: dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0
    sse_read_timeout: float = 300.0
    terminate_on_close: bool = True
    ssl_verify: bool = True

    @property
    def transport(self) -> str:
        return "streamable_http"

    def to_langchain_connection(self) -> dict[str, Any]:
        if not self.name.strip():
            raise ValueError("MCP streamable_http connection requires name")
        if not self.url.strip():
            raise ValueError(f"MCP streamable_http connection {self.name} requires url")
        connection = {
            "transport": "streamable_http",
            "url": self.url,
            "headers": dict(self.headers),
            "session_kwargs": self.session_kwargs,
            "timeout": timedelta(seconds=float(self.timeout)),
            "sse_read_timeout": timedelta(seconds=float(self.sse_read_timeout)),
            "terminate_on_close": self.terminate_on_close,
        }
        if not self.ssl_verify:
            connection["httpx_client_factory"] = _create_insecure_httpx_client
        return connection


class MCPListToolAdapter:
    def __init__(self, client: "MCPToolClient"):
        self.client = client

    def openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": MCP_LIST_TOOL_NAME,
                "description": "List MCP servers configured for this chat and the MCP tools currently available from them.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }

    async def invoke(self, arguments: dict[str, Any]) -> str:
        return json.dumps(self.client.tools_summary(), sort_keys=True)


@dataclass
class MCPToolAdapter:
    server_name: str
    exposed_name: str
    tool: Any
    read_only: bool = False

    @property
    def server_tool_name(self) -> str:
        return str(getattr(self.tool, "name", self.exposed_name))

    def openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.exposed_name,
                "description": self._description(),
                "parameters": self._parameters(),
            },
        }

    async def invoke(self, arguments: dict[str, Any], confirmed: bool = False) -> str:
        if not self.read_only and not confirmed:
            raise MCPConfirmationRequired(self, arguments)
        result = await self.tool.ainvoke(arguments)
        return serialize_tool_result(result)

    def confirmation_metadata(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "pending",
            "server_name": self.server_name,
            "tool_name": self.exposed_name,
            "server_tool_name": self.server_tool_name,
            "arguments": arguments,
            "description": self._description(),
            "parameters": self._parameters(),
            "annotations": self._annotations(),
            "read_only": self.read_only,
        }

    def _description(self) -> str:
        description = getattr(self.tool, "description", "") or self.server_tool_name
        confirmation_note = "Read-only tool." if self.read_only else (
            "Call this tool when appropriate; Mythic automatically handles the required operator confirmation."
        )
        return f"MCP server {self.server_name}: {description} {confirmation_note}"

    def _parameters(self) -> dict[str, Any]:
        args_schema = getattr(self.tool, "args_schema", None)
        if args_schema is not None:
            if hasattr(args_schema, "model_json_schema"):
                schema = args_schema.model_json_schema()
            elif hasattr(args_schema, "schema"):
                schema = args_schema.schema()
            else:
                schema = None
            if isinstance(schema, dict):
                schema.setdefault("type", "object")
                schema.setdefault("properties", {})
                return schema
        args = getattr(self.tool, "args", None)
        if isinstance(args, dict):
            return {"type": "object", "properties": args, "required": []}
        return {"type": "object", "properties": {}, "required": []}

    def _annotations(self) -> dict[str, Any]:
        annotations = getattr(self.tool, "annotations", None)
        if annotations is None and isinstance(getattr(self.tool, "metadata", None), dict):
            annotations = self.tool.metadata.get("annotations")
        return jsonable_dict(annotations)


class MCPToolClient:
    """Connects typed MCP server definitions and exposes OpenAI-style tools."""

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.sessions = []
        self.tools: list[MCPToolAdapter] = []
        self.tools_by_name: dict[str, Any] = {}
        self.server_configs: dict[str, dict[str, Any]] = {}
        self.list_tool = MCPListToolAdapter(self)
        self.tools_by_name[MCP_LIST_TOOL_NAME] = self.list_tool

    @classmethod
    async def create(cls, connections: list[MCPConnection] | tuple[MCPConnection, ...] | None = None):
        client = cls()
        try:
            for connection in connections or []:
                await client._connect_server(connection)
        except Exception:
            await client.close()
            raise
        return client

    def openai_tools(self) -> list[dict[str, Any]]:
        return [self.list_tool.openai_schema()] + [tool.openai_schema() for tool in self.tools]

    async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> str:
        return await self._invoke(tool_name, arguments, confirmed=False)

    async def invoke_confirmed(self, tool_name: str, arguments: dict[str, Any], server_name: str = "") -> str:
        return await self._invoke(tool_name, arguments, confirmed=True, server_name=server_name)

    async def _invoke(
            self,
            tool_name: str,
            arguments: dict[str, Any],
            confirmed: bool,
            server_name: str = "") -> str:
        tool = self.tools_by_name.get(tool_name)
        if not tool:
            return f"Error: unknown MCP tool {tool_name}"
        if isinstance(tool, MCPToolAdapter) and server_name and tool.server_name != server_name:
            return f"Error: MCP tool {tool_name} is not from server {server_name}"
        try:
            if isinstance(tool, MCPToolAdapter):
                return await tool.invoke(arguments, confirmed=confirmed)
            return await tool.invoke(arguments)
        except MCPConfirmationRequired:
            raise
        except Exception as e:
            logger.exception(f"MCP tool {tool_name} failed: {e}")
            return f"Error executing MCP tool {tool_name}: {e}"

    async def close(self) -> None:
        try:
            await self.exit_stack.aclose()
        except Exception as e:
            logger.warning(f"Failed to close MCP session context: {e}")
        self.exit_stack = AsyncExitStack()
        self.sessions = []
        self.server_configs = {}

    def tools_summary(self) -> dict[str, Any]:
        servers: dict[str, dict[str, Any]] = {}
        for name, config in self.server_configs.items():
            servers[name] = {
                "name": name,
                "transport": config.get("transport", "unknown"),
                "read_only_tools": config.get("read_only_tools", []),
                "tool_count": 0,
                "tools": [],
            }
        for adapter in self.tools:
            server = servers.setdefault(adapter.server_name, {
                "name": adapter.server_name,
                "transport": "unknown",
                "read_only_tools": [],
                "tool_count": 0,
                "tools": [],
            })
            server["tools"].append({
                "name": adapter.exposed_name,
                "server_tool_name": adapter.server_tool_name,
                "read_only": adapter.read_only,
                "requires_confirmation": not adapter.read_only,
                "description": adapter._description(),
                "parameters": adapter._parameters(),
                "annotations": adapter._annotations(),
            })
            server["tool_count"] = len(server["tools"])
        return {
            "connected_servers": len(servers),
            "total_mcp_tools": len(self.tools),
            "servers": list(servers.values()),
        }

    async def _connect_server(self, connection_definition: MCPConnection) -> None:
        try:
            from langchain_mcp_adapters.sessions import create_session
            from langchain_mcp_adapters.tools import load_mcp_tools
        except Exception as e:
            raise RuntimeError("MCP support requires langchain-mcp-adapters to be installed") from e

        connection = connection_definition.to_langchain_connection()
        try:
            session = await self.exit_stack.enter_async_context(create_session(connection))
            await session.initialize()
            loaded_tools = await load_mcp_tools(session, connection=connection)
        except Exception as e:
            raise MCPConnectionError(format_mcp_connection_error(connection_definition, connection, e)) from e
        self.sessions.append(session)
        read_only_tools = set(connection_definition.read_only_tools)
        self.server_configs[connection_definition.name] = {
            "transport": connection_definition.transport,
            "read_only_tools": sorted(read_only_tools),
        }
        for tool in loaded_tools:
            server_tool_name = str(getattr(tool, "name", "tool"))
            exposed_name = unique_tool_name(connection_definition.name, server_tool_name, set(self.tools_by_name))
            adapter = MCPToolAdapter(
                server_name=connection_definition.name,
                exposed_name=exposed_name,
                tool=tool,
                read_only=server_tool_name in read_only_tools,
            )
            self.tools.append(adapter)
            self.tools_by_name[exposed_name] = adapter
        logger.info(f"Loaded {len(loaded_tools)} MCP tools from server {connection_definition.name}")


def format_mcp_connection_error(
        definition: MCPConnection | str,
        connection: dict[str, Any],
        error: Exception) -> str:
    name = definition if isinstance(definition, str) else definition.name
    transport = connection.get("transport", "unknown")
    if transport == "streamable_http":
        target = connection.get("url", "unknown URL")
        return (
            f"Failed to connect to MCP server {name} with streamable_http at {target}: {error}. "
            "Make sure that URL is reachable from inside the chat container, not just from the Mythic host."
        )
    if transport == "stdio":
        command = " ".join([str(connection.get("command", "")), *[str(arg) for arg in connection.get("args") or []]]).strip()
        return f"Failed to start MCP server {name} with stdio command `{command}`: {error}"
    return f"Failed to connect to MCP server {name} with transport {transport}: {error}"


def unique_tool_name(server_name: str, tool_name: str, existing: set[str]) -> str:
    raw_name = f"mcp_{server_name}_{tool_name}"
    base_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", raw_name).strip("_") or "mcp_tool"
    base_name = base_name[:64].rstrip("_") or "mcp_tool"
    if base_name not in existing:
        return base_name
    for index in range(2, 1000):
        suffix = f"_{index}"
        candidate = f"{base_name[:64 - len(suffix)]}{suffix}".rstrip("_")
        if candidate not in existing:
            return candidate
    raise ValueError(f"failed to create unique MCP tool name for {server_name}:{tool_name}")


def serialize_tool_result(result: Any) -> str:
    if isinstance(result, str):
        return result
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    elif hasattr(result, "dict"):
        result = result.dict()
    return json.dumps(result, sort_keys=True, default=str)


def jsonable_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    elif hasattr(value, "dict"):
        value = value.dict()
    if isinstance(value, dict):
        return json.loads(json.dumps(value, default=str))
    return {}


def _create_insecure_httpx_client(**kwargs):
    try:
        import httpx
    except Exception as e:
        raise RuntimeError("MCP streamable_http ssl_verify=False requires httpx to be installed") from e
    kwargs.pop("verify", None)
    return httpx.AsyncClient(verify=False, **kwargs)
