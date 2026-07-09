import importlib.util
from pathlib import Path
import sys
import types
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "mythic_container"
RPC_ROOT = PACKAGE_ROOT / "MythicGoRPC"


class StubLogger:
    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


mythic_package = types.ModuleType("mythic_container")
mythic_package.__path__ = [str(PACKAGE_ROOT)]
mythic_package.RabbitmqConnection = None
sys.modules["mythic_container"] = mythic_package

logging_module = types.ModuleType("mythic_container.logging")
logging_module.logger = StubLogger()
sys.modules["mythic_container.logging"] = logging_module


def load_rpc_module(name):
    spec = importlib.util.spec_from_file_location(
        f"mythic_container.MythicGoRPC.{name}",
        RPC_ROOT / f"{name}.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


callback_create = load_rpc_module("send_mythic_rpc_callback_create")
callback_update = load_rpc_module("send_mythic_rpc_callback_update")
file_update = load_rpc_module("send_mythic_rpc_file_update")
proxy_start = load_rpc_module("send_mythic_rpc_proxy_start")
task_create = load_rpc_module("send_mythic_rpc_task_create")
task_create_subtask = load_rpc_module("send_mythic_rpc_task_create_subtask")
task_create_subtask_group = load_rpc_module("send_mythic_rpc_task_create_subtask_group")


class MythicGoRPCContractTests(unittest.TestCase):
    def test_callback_create_serializes_current_fields(self):
        message = callback_create.MythicRPCCallbackCreateMessage(
            PayloadUUID="payload-uuid",
            C2ProfileName="http",
            Ip="127.0.0.1",
            IPs=["127.0.0.1", "10.1.2.3"],
            Description="created from test",
        )

        serialized = message.to_json()
        self.assertEqual(serialized["ip"], "127.0.0.1")
        self.assertEqual(serialized["ips"], ["127.0.0.1", "10.1.2.3"])
        self.assertEqual(serialized["description"], "created from test")

    def test_callback_create_response_accepts_current_and_legacy_ids(self):
        response = callback_create.MythicRPCCallbackCreateMessageResponse(
            success=True,
            agent_callback_id="agent-callback-id",
            callback_id=12,
            callback_display_id=34,
        )

        self.assertTrue(response.Success)
        self.assertEqual(response.AgentCallbackID, "agent-callback-id")
        self.assertEqual(response.CallbackUUID, "agent-callback-id")
        self.assertEqual(response.CallbackID, 12)
        self.assertEqual(response.CallbackDisplayID, 34)

        legacy_response = callback_create.MythicRPCCallbackCreateMessageResponse(
            success=True,
            callback_uuid="legacy-agent-callback-id",
        )
        self.assertEqual(legacy_response.AgentCallbackID, "legacy-agent-callback-id")
        self.assertEqual(legacy_response.CallbackUUID, "legacy-agent-callback-id")

    def test_task_create_serializes_payload_type_and_reference_resolution(self):
        message = task_create.MythicRPCTaskCreateMessage(
            AgentCallbackID="agent-callback-id",
            CommandName="shell",
            PayloadTypeName="apollo",
            Params="whoami",
            ResolveTaskReferences=True,
        )

        serialized = message.to_json()
        self.assertEqual(serialized["payload_type_name"], "apollo")
        self.assertTrue(serialized["resolve_task_references"])

    def test_subtask_serializes_payload_type_and_reference_resolution(self):
        message = task_create_subtask.MythicRPCTaskCreateSubtaskMessage(
            TaskID=1,
            CommandName="shell",
            PayloadTypeName="apollo",
            Params="hostname",
            ResolveTaskReferences=False,
        )

        serialized = message.to_json()
        self.assertEqual(serialized["payload_type_name"], "apollo")
        self.assertFalse(serialized["resolve_task_references"])

    def test_subtask_group_serializes_per_task_current_fields(self):
        group_task = task_create_subtask_group.MythicRPCTaskCreateSubtaskGroupTasks(
            CommandName="shell",
            PayloadTypeName="apollo",
            Params="id",
            ResolveTaskReferences=True,
        )
        message = task_create_subtask_group.MythicRPCTaskCreateSubtaskGroupMessage(
            TaskID=1,
            GroupName="group",
            Tasks=[group_task],
        )

        serialized_task = message.to_json()["tasks"][0]
        self.assertEqual(serialized_task["payload_type_name"], "apollo")
        self.assertTrue(serialized_task["resolve_task_references"])

    def test_file_update_serializes_replace_contents_for_go_byte_slice(self):
        message = file_update.MythicRPCFileUpdateMessage(
            AgentFileID="file-id",
            ReplaceContents=b"new file contents",
            AppendContents=b" more",
        )

        serialized = message.to_json()
        self.assertEqual(serialized["replace_contents"], "bmV3IGZpbGUgY29udGVudHM=")
        self.assertEqual(serialized["append_contents"], "IG1vcmU=")

    def test_callback_update_serializes_ips(self):
        message = callback_update.MythicRPCCallbackUpdateMessage(
            CallbackID=12,
            IP="127.0.0.1",
            IPs=["127.0.0.1", "10.1.2.3"],
        )

        serialized = message.to_json()
        self.assertEqual(serialized["ip"], "127.0.0.1")
        self.assertEqual(serialized["ips"], ["127.0.0.1", "10.1.2.3"])

    def test_proxy_start_uses_current_lowercase_credentials(self):
        message = proxy_start.MythicRPCProxyStartMessage(
            TaskID=1,
            PortType=proxy_start.CALLBACK_PORT_TYPE_SOCKS,
            Username="alice",
            Password="secret",
        )

        serialized = message.to_json()
        self.assertEqual(serialized["username"], "alice")
        self.assertEqual(serialized["password"], "secret")
        self.assertNotIn("Username", serialized)
        self.assertNotIn("Password", serialized)


if __name__ == "__main__":
    unittest.main()
