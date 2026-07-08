import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "mythic_container"
mythic_package = types.ModuleType("mythic_container")
mythic_package.__path__ = [str(PACKAGE_ROOT)]
sys.modules["mythic_container"] = mythic_package
logging_module = types.ModuleType("mythic_container.logging")
logging_module.logger = types.SimpleNamespace(
    exception=lambda *args, **kwargs: None,
    warning=lambda *args, **kwargs: None,
    info=lambda *args, **kwargs: None,
)
sys.modules["mythic_container.logging"] = logging_module

spec = importlib.util.spec_from_file_location(
    "mythic_container.chat_mcp",
    PACKAGE_ROOT / "chat_mcp.py",
)
chat_mcp = importlib.util.module_from_spec(spec)
sys.modules["mythic_container.chat_mcp"] = chat_mcp
spec.loader.exec_module(chat_mcp)

MCPConfirmationRequired = chat_mcp.MCPConfirmationRequired
MCPStdioConnection = chat_mcp.MCPStdioConnection
MCPStreamableHTTPConnection = chat_mcp.MCPStreamableHTTPConnection
MCPToolAdapter = chat_mcp.MCPToolAdapter
MCPToolClient = chat_mcp.MCPToolClient
format_mcp_connection_error = chat_mcp.format_mcp_connection_error
unique_tool_name = chat_mcp.unique_tool_name


class DummyTool:
    name = "write_file"
    description = "write something"

    async def ainvoke(self, arguments):
        return {"ok": True, "arguments": arguments}


class ChatMCPTests(unittest.TestCase):
    def test_streamable_http_connection_converts_to_langchain_shape(self):
        connection = MCPStreamableHTTPConnection(
            name="docs",
            url="http://docs/mcp",
            headers={"Authorization": "Bearer token"},
            read_only_tools=("search",),
        )

        converted = connection.to_langchain_connection()
        self.assertEqual(converted["transport"], "streamable_http")
        self.assertEqual(converted["headers"]["Authorization"], "Bearer token")
        self.assertEqual(connection.read_only_tools, ("search",))

    def test_stdio_connection_converts_to_langchain_shape(self):
        connection = MCPStdioConnection(
            name="local",
            command="python3",
            args=("-m", "server"),
            env={"TOKEN": "abc"},
        )

        converted = connection.to_langchain_connection()
        self.assertEqual(converted["transport"], "stdio")
        self.assertEqual(converted["args"], ["-m", "server"])
        self.assertEqual(converted["env"]["TOKEN"], "abc")

    def test_tool_confirmation_and_read_only_execution(self):
        async def run_check():
            guarded = MCPToolAdapter(
                server_name="docs",
                exposed_name="mcp_docs_write_file",
                tool=DummyTool(),
                read_only=False,
            )
            with self.assertRaises(MCPConfirmationRequired) as caught:
                await guarded.invoke({"path": "x"})
            input_request = caught.exception.to_input_request()
            self.assertEqual(input_request["input_type"], "approval")
            self.assertEqual(input_request["data"]["tool_name"], "mcp_docs_write_file")
            self.assertFalse(input_request["data"]["read_only"])

            read_only = MCPToolAdapter(
                server_name="docs",
                exposed_name="mcp_docs_write_file",
                tool=DummyTool(),
                read_only=True,
            )
            return await read_only.invoke({"path": "x"})

        result = asyncio.run(run_check())
        self.assertIn("ok", result)

    def test_tool_client_includes_list_tool_without_connections(self):
        client = MCPToolClient()

        schemas = client.openai_tools()
        self.assertEqual(schemas[0]["function"]["name"], "mcp_list_available_tools")
        self.assertEqual(client.tools_summary()["connected_servers"], 0)

    def test_unique_tool_name_and_connection_error_are_container_neutral(self):
        existing = {"mcp_docs_write_file"}
        self.assertEqual(unique_tool_name("docs", "write_file", existing), "mcp_docs_write_file_2")

        connection = MCPStreamableHTTPConnection(name="docs", url="http://docs/mcp")
        message = format_mcp_connection_error(
            connection,
            connection.to_langchain_connection(),
            RuntimeError("All connection attempts failed"),
        )
        self.assertIn("inside the chat container", message)


if __name__ == "__main__":
    unittest.main()
