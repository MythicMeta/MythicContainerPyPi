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


class HelperChat(Chat):
    name = "helper_chat"


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

    def test_metadata_serializes_slash_commands(self):
        metadata = ChatModelMetadata(
            Provider="example",
            SlashCommands=[
                ChatSlashCommandDefinition(Name="summarize", Description="Summarize context"),
            ],
        )

        serialized = metadata.to_json()
        self.assertEqual(serialized["slash_commands"][0]["name"], "summarize")

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
        self.assertEqual(captured[-1]["metadata"]["input_requested"]["input_type"], "single_choice")
        self.assertFalse(captured[-1]["complete_request"])

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
