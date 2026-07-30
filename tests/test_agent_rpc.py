import unittest
from pathlib import Path
from unittest.mock import patch

import ujson

import mythic_container
from mythic_container import PayloadBuilder, agent_utils, mythic_service
from mythic_container.MythicCommandBase import (
    PTTaskAgentRPCMessage,
    PTTaskAgentRPCMessageResponse,
)


class FakeRabbitMQConnection:
    def __init__(self):
        self.messages = []

    async def SendDictDirectMessage(self, queue, body):
        self.messages.append((queue, body))


class AgentRPCTestPayload(PayloadBuilder.PayloadType):
    name = "agent-rpc-test"
    agent_path = Path(".")
    agent_code_path = Path(".")
    agent_browserscript_path = Path(".")

    def __init__(self):
        super().__init__()
        self.received = None

    async def agent_rpc(self, task, name, arguments):
        self.received = (task, name, arguments)
        return PTTaskAgentRPCMessageResponse(
            CallbackID=999,
            AgentTaskID="developer-supplied-id",
            Status="custom-status",
            Output={"echo": arguments},
        )


class InvalidAgentRPCTestPayload(AgentRPCTestPayload):
    async def agent_rpc(self, task, name, arguments):
        return {"status": "success"}


class RaisingAgentRPCTestPayload(AgentRPCTestPayload):
    async def agent_rpc(self, task, name, arguments):
        raise RuntimeError("boom")


class NonSerializableAgentRPCTestPayload(AgentRPCTestPayload):
    async def agent_rpc(self, task, name, arguments):
        return PTTaskAgentRPCMessageResponse(
            Status="success",
            Output=object(),
        )


class EmptyStatusAgentRPCTestPayload(AgentRPCTestPayload):
    async def agent_rpc(self, task, name, arguments):
        return PTTaskAgentRPCMessageResponse(
            Status="",
            Output={"ignored": True},
        )


class DefaultAgentRPCTestPayload(PayloadBuilder.PayloadType):
    name = "default-payload"
    agent_path = Path(".")
    agent_code_path = Path(".")
    agent_browserscript_path = Path(".")


class AgentRPCContractTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.original_payload_types = dict(PayloadBuilder.payloadTypes)
        self.original_connection = mythic_container.RabbitmqConnection
        PayloadBuilder.payloadTypes.clear()
        self.connection = FakeRabbitMQConnection()
        mythic_container.RabbitmqConnection = self.connection

    def tearDown(self):
        PayloadBuilder.payloadTypes.clear()
        PayloadBuilder.payloadTypes.update(self.original_payload_types)
        mythic_container.RabbitmqConnection = self.original_connection

    @staticmethod
    def request(arguments=None):
        return {
            "task": {
                "task": {
                    "id": 9,
                    "agent_task_id": "agent-task-uuid",
                    "command_name": "augment-command",
                },
                "callback": {
                    "id": 42,
                },
                "build_parameters": [],
                "commands": [],
                "payload": {},
                "c2info": [],
                "payload_type": "agent-rpc-test",
                "command_payload_type": "command-augment",
                "secrets": {},
            },
            "name": "lookup",
            "arguments": arguments,
        }

    async def test_wire_classes_preserve_arbitrary_json_values(self):
        request = PTTaskAgentRPCMessage(**self.request(
            arguments={"nested": ["one", 2, True, None]}
        ))
        self.assertEqual(request.Name, "lookup")
        self.assertEqual(
            request.Arguments,
            {"nested": ["one", 2, True, None]},
        )
        self.assertEqual(request.TaskData.PayloadType, "agent-rpc-test")
        self.assertEqual(request.TaskData.CommandPayloadType, "command-augment")

        response = PTTaskAgentRPCMessageResponse(
            CallbackID=42,
            AgentTaskID="agent-task-uuid",
            Status="success",
            Output=None,
        )
        self.assertEqual(response.to_json(), {
            "callback_id": 42,
            "agent_task_id": "agent-task-uuid",
            "status": "success",
            "output": None,
        })

    async def test_agent_rpc_invokes_callback_payload_and_normalizes_ids(self):
        payload = AgentRPCTestPayload()
        PayloadBuilder.payloadTypes[payload.name] = payload
        arguments = {"value": [1, "two", None]}

        await agent_utils.agentRPC(ujson.dumps(self.request(arguments)).encode())

        self.assertIsNotNone(payload.received)
        task, name, received_arguments = payload.received
        self.assertEqual(task.PayloadType, "agent-rpc-test")
        self.assertEqual(task.CommandPayloadType, "command-augment")
        self.assertEqual(name, "lookup")
        self.assertEqual(received_arguments, arguments)
        self.assertEqual(len(self.connection.messages), 1)
        queue, body = self.connection.messages[0]
        self.assertEqual(queue, mythic_container.PT_TASK_AGENT_RPC_RESPONSE)
        self.assertEqual(body["callback_id"], 42)
        self.assertEqual(body["agent_task_id"], "agent-task-uuid")
        self.assertEqual(body["status"], "custom-status")
        self.assertEqual(body["output"], {"echo": arguments})
        self.assertEqual(
            mythic_service.getRoutingKey(payload.name, mythic_container.PT_TASK_AGENT_RPC),
            "agent-rpc-test_pt_task_agent_rpc",
        )

    async def test_invalid_hook_return_becomes_correlated_error(self):
        payload = InvalidAgentRPCTestPayload()
        PayloadBuilder.payloadTypes[payload.name] = payload

        with patch.object(agent_utils.logger, "exception"):
            await agent_utils.agentRPC(ujson.dumps(self.request({})).encode())

        _, body = self.connection.messages[0]
        self.assertEqual(body["callback_id"], 42)
        self.assertEqual(body["agent_task_id"], "agent-task-uuid")
        self.assertEqual(body["status"], "error")
        self.assertIn("must return PTTaskAgentRPCMessageResponse", body["output"])

    async def test_hook_exception_becomes_correlated_error(self):
        payload = RaisingAgentRPCTestPayload()
        PayloadBuilder.payloadTypes[payload.name] = payload

        with patch.object(agent_utils.logger, "exception"):
            await agent_utils.agentRPC(ujson.dumps(self.request({})).encode())

        _, body = self.connection.messages[0]
        self.assertEqual(body["callback_id"], 42)
        self.assertEqual(body["agent_task_id"], "agent-task-uuid")
        self.assertEqual(body["status"], "error")
        self.assertIn("RuntimeError: boom", body["output"])

    async def test_non_serializable_output_becomes_correlated_error(self):
        payload = NonSerializableAgentRPCTestPayload()
        PayloadBuilder.payloadTypes[payload.name] = payload

        await agent_utils.agentRPC(ujson.dumps(self.request(None)).encode())

        _, body = self.connection.messages[0]
        self.assertEqual(body["callback_id"], 42)
        self.assertEqual(body["agent_task_id"], "agent-task-uuid")
        self.assertEqual(body["status"], "error")
        self.assertIn("Failed to serialize agent_rpc output", body["output"])

    async def test_non_json_numeric_output_becomes_correlated_error(self):
        response = PTTaskAgentRPCMessageResponse(
            CallbackID=42,
            AgentTaskID="agent-task-uuid",
            Status="success",
            Output=float("nan"),
        )

        await agent_utils._send_agent_rpc_response(response)

        _, body = self.connection.messages[0]
        self.assertEqual(body["status"], "error")
        self.assertIn("Failed to serialize agent_rpc output", body["output"])

    async def test_empty_status_becomes_correlated_error(self):
        payload = EmptyStatusAgentRPCTestPayload()
        PayloadBuilder.payloadTypes[payload.name] = payload

        await agent_utils.agentRPC(ujson.dumps(self.request(None)).encode())

        _, body = self.connection.messages[0]
        self.assertEqual(body["callback_id"], 42)
        self.assertEqual(body["agent_task_id"], "agent-task-uuid")
        self.assertEqual(body["status"], "error")
        self.assertIn("empty or non-string status", body["output"])

    async def test_default_hook_reports_not_implemented(self):
        payload = DefaultAgentRPCTestPayload()
        response = await payload.agent_rpc(
            task=PTTaskAgentRPCMessage(**self.request()).TaskData,
            name="lookup",
            arguments=None,
        )
        self.assertEqual(response.Status, "error")
        self.assertIn("not implemented", response.Output)


if __name__ == "__main__":
    unittest.main()
