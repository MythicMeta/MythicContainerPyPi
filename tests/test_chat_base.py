import asyncio
import base64
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "mythic_container"
mythic_package = types.ModuleType("mythic_container")
mythic_package.__path__ = [str(PACKAGE_ROOT)]
sys.modules["mythic_container"] = mythic_package
logging_module = types.ModuleType("mythic_container.logging")
logging_module.logger = types.SimpleNamespace(
    error=lambda *args, **kwargs: None,
    exception=lambda *args, **kwargs: None,
    info=lambda *args, **kwargs: None,
)
sys.modules["mythic_container.logging"] = logging_module

spec = importlib.util.spec_from_file_location(
    "mythic_container.ChatBase",
    PACKAGE_ROOT / "ChatBase.py",
)
ChatBase = importlib.util.module_from_spec(spec)
sys.modules["mythic_container.ChatBase"] = ChatBase
spec.loader.exec_module(ChatBase)

Chat = ChatBase.Chat
ChatAPITokenProvider = ChatBase.ChatAPITokenProvider
ChatConfigView = ChatBase.ChatConfigView
ChatModelConfigurationOption = ChatBase.ChatModelConfigurationOption
ChatModelConfigurationOptionType = ChatBase.ChatModelConfigurationOptionType
ChatModelMetadata = ChatBase.ChatModelMetadata
ChatRequest = ChatBase.ChatRequest
ChatSecretView = ChatBase.ChatSecretView
ChatSlashCommandDefinition = ChatBase.ChatSlashCommandDefinition
ChatInputChoice = ChatBase.ChatInputChoice
ChatChannelMetadataUpdate = ChatBase.ChatChannelMetadataUpdate


class HelperChat(Chat):
    name = "helper_chat"


class IconBytesChat(Chat):
    name = "icon_bytes_chat"
    agent_icon_bytes = b"<svg>light</svg>"
    dark_mode_agent_icon_bytes = b"<svg>dark</svg>"


class IconFallbackChat(Chat):
    name = "icon_fallback_chat"
    agent_icon_bytes = b"<svg>light</svg>"


class ChatBaseTests(unittest.TestCase):
    def test_request_preserves_slash_command(self):
        request = ChatRequest(
            container_name="helper_chat",
            prompt="run it",
            slash_command={
                "name": "explain",
                "argument": "callbacks",
                "raw": "/explain callbacks",
                "source": "operator",
            },
        )

        self.assertEqual(request.SlashCommand.Name, "explain")
        self.assertEqual(request.to_json()["slash_command"]["argument"], "callbacks")

    def test_request_preserves_input_response(self):
        request = ChatRequest(
            container_name="helper_chat",
            input_response={
                "action": "select",
                "choice": {"id": "one", "label": "One"},
                "input_request_message_id": 44,
                "input_request": {"title": "Pick one"},
                "resolved_by": "alice",
            },
        )

        self.assertEqual(request.InputResponse.Action, "select")
        self.assertEqual(request.to_json()["input_response"]["choice"]["id"], "one")

    def test_request_preserves_delegation_fields(self):
        request = ChatRequest(
            container_name="helper_chat",
            delegation_id="delegation-1",
            delegation_name="BloodHound",
        )

        self.assertEqual(request.DelegationID, "delegation-1")
        self.assertEqual(request.DelegationName, "BloodHound")
        self.assertEqual(request.to_json()["delegation_id"], "delegation-1")
        self.assertEqual(request.to_json()["delegation_name"], "BloodHound")

    def test_config_option_serializes_json_string_schema(self):
        option = ChatModelConfigurationOption(
            Name="MCP",
            DisplayName="MCP",
            Type=ChatModelConfigurationOptionType.JSON,
            JSONStringSchema={"type": "object", "label": "MCP"},
            MinRows=12,
        )

        serialized = option.to_json()
        self.assertEqual(serialized["json_string_schema"]["label"], "MCP")
        self.assertEqual(serialized["min_rows"], 12)

    def test_config_option_serializes_display_as_chip(self):
        option = ChatModelConfigurationOption(
            Name="PROVIDER_MODEL",
            DisplayName="Provider",
            DisplayAsChip=True,
        )

        serialized = option.to_json()
        self.assertTrue(serialized["display_as_chip"])

    def test_chat_channel_metadata_update_shape(self):
        update = ChatChannelMetadataUpdate(
            OperationID=1,
            ChannelID=2,
            ContainerName="basic_chat",
            ChannelMetadata={
                "items": [
                    {"key": "total_cost", "value": 1.25, "format": "currency"},
                ],
            },
        )

        serialized = update.to_json()
        self.assertEqual(serialized["operation_id"], 1)
        self.assertEqual(serialized["channel_id"], 2)
        self.assertEqual(serialized["container_name"], "basic_chat")
        self.assertEqual(serialized["channel_metadata"]["items"][0]["key"], "total_cost")

    def test_chat_channel_metadata_update_preserves_color_shapes(self):
        update = ChatChannelMetadataUpdate(
            OperationID=1,
            ChannelID=2,
            ContainerName="basic_chat",
            ChannelMetadata={
                "items": [
                    {"key": "provider", "value": "LiteLLM", "color": "neutral"},
                    {"key": "accent", "value": "custom", "color": "#4f46e5"},
                    {
                        "key": "last_update",
                        "value": "2026-07-09 18:20 UTC",
                        "color": "info",
                        "click": "/stats",
                        "click_confirmation_text": "Run /stats to refresh metadata?",
                    },
                    {
                        "key": "usage",
                        "value": 91,
                        "color": {
                            "type": "scale",
                            "source": "value",
                            "stops": [
                                {"at": 0, "color": "success"},
                                {"at": 75, "color": "warning"},
                                {"at": 90, "color": "error"},
                            ],
                        },
                    },
                ],
            },
        )

        items = update.to_json()["channel_metadata"]["items"]
        self.assertEqual(items[0]["color"], "neutral")
        self.assertEqual(items[1]["color"], "#4f46e5")
        self.assertEqual(items[2]["click"], "/stats")
        self.assertIn("/stats", items[2]["click_confirmation_text"])
        self.assertEqual(items[3]["color"]["stops"][2]["color"], "error")

    def test_metadata_serializes_slash_commands(self):
        metadata = ChatModelMetadata(
            Provider="example",
            SlashCommands=[
                ChatSlashCommandDefinition(Name="summarize", Description="Summarize context"),
            ],
        )

        serialized = metadata.to_json()
        self.assertEqual(serialized["slash_commands"][0]["name"], "summarize")

    def test_sync_message_includes_base64_chat_icons_from_bytes(self):
        sync_message = IconBytesChat().get_sync_message()

        self.assertEqual(base64.b64decode(sync_message["agent_icon"]), b"<svg>light</svg>")
        self.assertEqual(base64.b64decode(sync_message["dark_mode_agent_icon"]), b"<svg>dark</svg>")

    def test_sync_message_uses_light_icon_for_missing_dark_icon(self):
        sync_message = IconFallbackChat().get_sync_message()

        self.assertEqual(sync_message["agent_icon"], sync_message["dark_mode_agent_icon"])
        self.assertEqual(base64.b64decode(sync_message["agent_icon"]), b"<svg>light</svg>")

    def test_sync_message_reads_chat_icons_from_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            light_icon = Path(temp_dir) / "light.svg"
            dark_icon = Path(temp_dir) / "dark.svg"
            light_icon.write_bytes(b"<svg>path-light</svg>")
            dark_icon.write_bytes(b"<svg>path-dark</svg>")

            class IconPathChat(Chat):
                name = "icon_path_chat"
                agent_icon_path = str(light_icon)
                dark_mode_agent_icon_path = str(dark_icon)

            sync_message = IconPathChat().get_sync_message()

        self.assertEqual(base64.b64decode(sync_message["agent_icon"]), b"<svg>path-light</svg>")
        self.assertEqual(base64.b64decode(sync_message["dark_mode_agent_icon"]), b"<svg>path-dark</svg>")

    def test_typed_config_and_secret_readers(self):
        request = ChatRequest(
            config={
                "URL": " http://provider/v1 ",
                "COUNT": "7",
                "ENABLED": "true",
                "OBJECT": {"ok": True},
            },
            secrets={"API_KEY": {"value": "secret-value"}},
        )

        config = ChatConfigView.from_request(request)
        secrets = ChatSecretView.from_request(request)
        self.assertEqual(config.required_text("URL"), "http://provider/v1")
        self.assertEqual(config.integer("COUNT"), 7)
        self.assertTrue(config.boolean("ENABLED"))
        self.assertEqual(config.dict_value("OBJECT"), {"ok": True})
        self.assertEqual(secrets.required_text("API_KEY"), "secret-value")

    def test_response_helpers_shape_chat_responses(self):
        async def run_check():
            captured = []
            original = ChatBase.SendMythicRPCChatResponse

            async def fake_send(response):
                captured.append(response.to_json())

            ChatBase.SendMythicRPCChatResponse = fake_send
            try:
                chat = HelperChat()
                request = ChatRequest(
                    operation_id=1,
                    request_id=2,
                    prompt="hello",
                )
                await chat.send_streaming(request, "assistant:test", metadata={"phase": "start"})
                await chat.send_delta(request, "assistant:test", "hi", metadata={"phase": "delta"})
                await chat.send_complete(request, "assistant:test", metadata={"phase": "done"})
                await chat.send_input_request(request, {
                    "status": "pending",
                    "input_type": "approval",
                    "title": "Approve write",
                    "prompt": "Approve writing x?",
                    "data": {"path": "x"},
                }, metadata={"phase": "confirm"})
                await chat.send_input_request(request, {
                    "status": "pending",
                    "input_type": "approval",
                    "title": "Approve write",
                    "prompt": "Approve writing x again?",
                    "data": {"path": "x"},
                })
                await chat.send_input_request(request, {
                    "status": "pending",
                    "input_type": "approval",
                    "title": "Approve write",
                    "prompt": "Update this same request?",
                }, response_key="input_requested:stable")
                await chat.send_single_choice_request(
                    request,
                    title="Pick one",
                    prompt="Choose an option",
                    choices=[ChatInputChoice(id="a", label="A", data={"value": 1})],
                )
            finally:
                ChatBase.SendMythicRPCChatResponse = original
            return captured

        captured = asyncio.run(run_check())
        self.assertEqual(captured[0]["status"], "streaming")
        self.assertTrue(captured[1]["is_delta"])
        self.assertTrue(captured[2]["complete"])
        self.assertEqual(captured[3]["metadata"]["special_type"], "input_requested")
        self.assertFalse(captured[3]["complete_request"])
        self.assertTrue(captured[3]["response_key"].startswith("input_requested:"))
        self.assertTrue(captured[4]["response_key"].startswith("input_requested:"))
        self.assertNotEqual(captured[3]["response_key"], captured[4]["response_key"])
        self.assertEqual(captured[5]["response_key"], "input_requested:stable")
        self.assertEqual(captured[-1]["metadata"]["input_requested"]["input_type"], "single_choice")
        self.assertFalse(captured[-1]["complete_request"])

    def test_turn_metadata_carries_delegation_fields(self):
        chat = HelperChat()
        request = ChatRequest(
            operation_id=1,
            request_id=2,
            delegation_id="delegation-1",
            delegation_name="BloodHound",
        )
        turn = chat.turn_context(request, response_key="assistant:test", metadata={"phase": "start"})

        metadata = turn._metadata({"phase": "delta"})

        self.assertEqual(metadata["phase"], "delta")
        self.assertEqual(metadata["delegation_id"], "delegation-1")
        self.assertEqual(metadata["delegation_name"], "BloodHound")

    def test_turn_metadata_allows_explicit_delegation_override(self):
        chat = HelperChat()
        request = ChatRequest(
            operation_id=1,
            request_id=2,
            delegation_id="request-delegation",
            delegation_name="Request Name",
        )
        turn = chat.turn_context(request, response_key="assistant:test")

        metadata = turn._metadata({
            "delegation_id": "explicit-delegation",
            "delegation_name": "Explicit Name",
        })

        self.assertEqual(metadata["delegation_id"], "explicit-delegation")
        self.assertEqual(metadata["delegation_name"], "Explicit Name")

    def test_subagent_status_helper_shapes_special_card(self):
        async def run_check():
            captured = []
            original = ChatBase.SendMythicRPCChatResponse

            async def fake_send(response):
                captured.append(response.to_json())

            ChatBase.SendMythicRPCChatResponse = fake_send
            try:
                chat = HelperChat()
                request = ChatRequest(
                    operation_id=1,
                    request_id=2,
                    delegation_id="delegation-1",
                    delegation_name="BloodHound",
                )
                turn = chat.turn_context(request, response_key="assistant:test")
                await turn.send_subagent_status(
                    title="BloodHound",
                    prompt="List domains and summarize trust relationships.",
                    status="finished",
                    tool_count=3,
                    tool_total=13,
                    icon="BH",
                    content="Found two domains.",
                    complete=True,
                )
            finally:
                ChatBase.SendMythicRPCChatResponse = original
            return captured

        captured = asyncio.run(run_check())
        self.assertEqual(captured[0]["response_key"], "subagent:delegation-1")
        self.assertEqual(captured[0]["status"], "complete")
        self.assertTrue(captured[0]["complete"])
        self.assertEqual(captured[0]["content"], "Found two domains.")
        self.assertEqual(captured[0]["metadata"]["special_type"], "subagent")
        self.assertEqual(captured[0]["metadata"]["delegation_id"], "delegation-1")
        self.assertEqual(captured[0]["metadata"]["delegation_name"], "BloodHound")
        self.assertEqual(captured[0]["metadata"]["subagent"]["title"], "BloodHound")
        self.assertEqual(captured[0]["metadata"]["subagent"]["prompt"], "List domains and summarize trust relationships.")
        self.assertEqual(captured[0]["metadata"]["subagent"]["status"], "finished")
        self.assertEqual(captured[0]["metadata"]["subagent"]["tool_count"], 3)
        self.assertEqual(captured[0]["metadata"]["subagent"]["tool_total"], 13)
        self.assertEqual(captured[0]["metadata"]["subagent"]["icon"], "BH")

    def test_update_channel_metadata_helper_uses_current_request(self):
        async def run_check():
            captured = []
            original = ChatBase.SendMythicRPCChatChannelMetadataUpdate

            async def fake_send(update):
                captured.append(update.to_json())
                return ChatBase.ChatChannelMetadataUpdateResponse(success=True)

            ChatBase.SendMythicRPCChatChannelMetadataUpdate = fake_send
            try:
                chat = HelperChat()
                request = ChatRequest(
                    operation_id=1,
                    channel_id=2,
                    container_name="helper_chat",
                )
                response = await chat.update_channel_metadata(request, {
                    "items": [{"key": "weekly_tokens", "value": 12}],
                })
            finally:
                ChatBase.SendMythicRPCChatChannelMetadataUpdate = original
            return captured, response

        captured, response = asyncio.run(run_check())
        self.assertTrue(response.Success)
        self.assertEqual(captured[0]["operation_id"], 1)
        self.assertEqual(captured[0]["channel_id"], 2)
        self.assertEqual(captured[0]["container_name"], "helper_chat")
        self.assertEqual(captured[0]["channel_metadata"]["items"][0]["key"], "weekly_tokens")

    def test_run_chat_turn_wraps_streaming_completion_and_errors(self):
        async def run_check():
            captured = []
            original = ChatBase.SendMythicRPCChatResponse

            async def fake_send(response):
                captured.append(response.to_json())

            ChatBase.SendMythicRPCChatResponse = fake_send
            try:
                chat = HelperChat()
                request = ChatRequest(
                    operation_id=1,
                    request_id=2,
                    prompt="hello",
                )

                async def successful(turn):
                    turn.metadata["during"] = "handler"
                    await turn.send_delta("hi")
                    return {"done": True}

                await chat.run_chat_turn(request, successful, response_key="assistant:success", metadata={"phase": "start"})

                async def failing(turn):
                    raise RuntimeError("provider exploded")

                await chat.run_chat_turn(request, failing, response_key="assistant:error", metadata={"phase": "error"})
            finally:
                ChatBase.SendMythicRPCChatResponse = original
            return captured

        captured = asyncio.run(run_check())
        self.assertEqual(captured[0]["status"], "streaming")
        self.assertEqual(captured[0]["response_key"], "assistant:success")
        self.assertTrue(captured[0]["is_delta"])
        self.assertTrue(captured[1]["complete"])
        self.assertTrue(captured[1]["complete_request"])
        self.assertEqual(captured[1]["metadata"]["during"], "handler")
        self.assertTrue(captured[1]["metadata"]["done"])
        self.assertEqual(captured[-1]["status"], "error")
        self.assertEqual(captured[-1]["error"], "provider exploded")
        self.assertTrue(captured[-1]["complete_request"])

    def test_message_builder_normalizes_context(self):
        chat = HelperChat()
        request = ChatRequest(
            request_message_id=2,
            prompt="current prompt",
            context=[
                {"id": 1, "author_type": "operator", "sender_display_name": "alice", "message": "old"},
                {"id": 2, "author_type": "operator", "sender_display_name": "bob", "message": "skip me"},
                {"id": 3, "author_type": "ai", "sender_display_name": "helper", "message": "answer"},
            ],
        )

        messages = chat.build_chat_messages(request, system_prompt="system", max_context_messages=0)
        self.assertEqual(messages[0], {"role": "system", "content": "system"})
        self.assertEqual(messages[1], {"role": "user", "content": "alice: old"})
        self.assertEqual(messages[2], {"role": "assistant", "content": "answer"})
        self.assertEqual(messages[3], {"role": "user", "content": "bob: current prompt"})

    def test_chat_api_token_provider_cache_is_request_scoped(self):
        async def run_check():
            ChatAPITokenProvider._cache.clear()
            first = await ChatAPITokenProvider.create(1, 2, 3)
            second = await ChatAPITokenProvider.create(1, 2, 3)
            third = await ChatAPITokenProvider.create(1, 2, 4)
            return first, second, third

        first, second, third = asyncio.run(run_check())
        self.assertIs(first, second)
        self.assertIsNot(first, third)


if __name__ == "__main__":
    unittest.main()
