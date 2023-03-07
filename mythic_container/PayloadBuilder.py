from enum import Enum
from abc import abstractmethod
import base64
from .logging import logger
from . import MythicCommandBase
from collections.abc import Callable, Awaitable
import pathlib


class BuildStatus:
    Success = "success"
    Error = "error"


class SupportedOS:
    Windows = "Windows"
    MacOS = "macOS"
    Linux = "Linux"
    WebShell = "WebShell"
    Chrome = "Chrome"

    def __init__(self, os: str):
        self.os = os

    def __str__(self):
        return self.os


class BuildParameterType(str, Enum):
    String = "String"
    ChooseOne = "ChooseOne"
    Boolean = "Boolean"
    ChooseMultiple = "ChoiceMultiple"


class BuildParameter:
    def __init__(
            self,
            name: str,
            parameter_type: BuildParameterType = None,
            description: str = None,
            required: bool = None,
            verifier_regex: str = None,
            default_value: any = None,
            choices: [str] = None,
            value: any = None,
            verifier_func: callable = None,
    ):
        self.name = name
        self.verifier_func = verifier_func
        self.parameter_type = (
            parameter_type if parameter_type is not None else MythicCommandBase.ParameterType.String
        )
        self.description = description if description is not None else ""
        self.required = required if required is not None else True
        self.verifier_regex = verifier_regex if verifier_regex is not None else ""
        self.default_value = default_value
        if value is None:
            self.value = default_value
        else:
            self.value = value
        self.choices = choices

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def parameter_type(self):
        return self._parameter_type

    @parameter_type.setter
    def parameter_type(self, parameter_type):
        self._parameter_type = parameter_type

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def required(self):
        return self._required

    @required.setter
    def required(self, required):
        self._required = required

    @property
    def verifier_regex(self):
        return self._verifier_regex

    @verifier_regex.setter
    def verifier_regex(self, verifier_regex):
        self._verifier_regex = verifier_regex

    @property
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, default_value):
        self._default_value = default_value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            self._value = value
        else:
            if self.verifier_func is not None:
                self.verifier_func(value)
                self._value = value
            else:
                if isinstance(value, str) and value.lower() == "false":
                    self._value = False
                elif isinstance(value, str) and value.lower() == "true":
                    self._value = True
                else:
                    self._value = value

    def to_json(self):
        return {
            "name": self._name,
            "parameter_type": self._parameter_type.value,
            "description": self._description,
            "required": self._required,
            "verifier_regex": self._verifier_regex,
            "parameter": self._default_value,
            "choices": self.choices,
            "default_value": self.default_value
        }


class C2ProfileParameters:
    def __init__(self, c2profile: dict, parameters: dict = None):
        self.parameters = {}
        self.c2profile = c2profile
        if parameters is not None:
            self.parameters = parameters

    def get_parameters_dict(self):
        return self.parameters

    def get_c2profile(self):
        return self.c2profile


class CommandList:
    def __init__(self, commands: [str] = None):
        self.commands = []
        if commands is not None:
            self.commands = commands

    def get_commands(self) -> [str]:
        return self.commands

    def remove_command(self, command: str):
        self.commands.remove(command)

    def add_command(self, command: str):
        for c in self.commands:
            if c == command:
                return
        self.commands.append(command)

    def clear(self):
        self.commands = []


class BuildResponse:
    def __init__(self, status: BuildStatus, payload: bytes = None, build_message: str = None, build_stderr: str = None,
                 build_stdout: str = None, updated_command_list: [str] = None):
        self.status = status
        self.payload = payload if payload is not None else b""
        self.build_message = build_message if build_message is not None else ""
        self.build_stderr = build_stderr if build_stderr is not None else ""
        self.build_stdout = build_stdout if build_stdout is not None else ""
        self.updated_command_list = updated_command_list

    def get_status(self) -> BuildStatus:
        return self.status

    def set_status(self, status: BuildStatus):
        self.status = status

    def get_payload(self) -> bytes:
        return self.payload

    def set_payload(self, payload: bytes):
        self.payload = payload

    def set_build_message(self, build_message: str):
        self.build_message = build_message

    def get_build_message(self) -> str:
        return self.build_message

    def set_build_stderr(self, build_stderr: str):
        self.build_stderr = build_stderr

    def get_build_stderr(self) -> str:
        return self.build_stderr

    def get_build_stdout(self) -> str:
        return self.build_stdout

    def set_build_stdout(self, build_stdout: str):
        self.build_stdout = build_stdout

    def get_updated_command_list(self):
        return self.updated_command_list

    def set_updated_command_list(self, command_list):
        self.updated_command_list = command_list


class BuildStep:

    def __init__(self,
                 step_name: str,
                 step_description: str):
        self.step_name = step_name
        self.step_description = step_description

    def to_json(self):
        return {
            "step_name": self.step_name,
            "step_description": self.step_description
        }

class PTOtherServiceRPCMessage:
    def __init__(self,
                 ServiceName: str = None,
                 service_name: str = None,
                 ServiceRPCFunction: str = None,
                 service_function: str = None,
                 ServiceRPCFunctionArguments: dict = None,
                 service_arguments: dict = None,
                 **kwargs):
        self.ServiceName = ServiceName
        if self.ServiceName is None:
            self.ServiceName = service_name
        self.ServiceRPCFunction = ServiceRPCFunction
        if self.ServiceRPCFunction is None:
            self.ServiceRPCFunction = service_function
        self.ServiceRPCFunctionArguments = ServiceRPCFunctionArguments
        if self.ServiceRPCFunctionArguments is None:
            self.ServiceRPCFunctionArguments = service_arguments
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "service_name": self.ServiceName,
            "service_function": self.ServiceRPCFunction,
            "service_arguments": self.ServiceRPCFunctionArguments
        }
class PTOtherServiceRPCMessageResponse:
    def __init__(self,
                 success: bool = None,
                 error: str = None,
                 result: dict = None,
                 Success: bool = None,
                 Error: str = None,
                 Result: dict = None,
                 **kwargs):
        self.Success = Success
        if self.Success is None:
            self.Success = success
        self.Error = Error
        if self.Error is None:
            self.Error = error
        self.Result = Result
        if self.Result is None:
            self.Result = result
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "result": self.Result
        }


class PayloadType:
    uuid: str = None
    c2info: [C2ProfileParameters] = None
    commands: CommandList = None
    wrapped_payload: str = None
    selected_os: str = None
    build_steps = []
    agent_icon_path: str = None
    agent_icon_bytes: bytes = None
    translation_container = None
    mythic_encrypts = True
    agent_path = None
    agent_code_path = None
    agent_browserscript_path = None
    custom_rpc_functions: dict[str, Callable[[PTOtherServiceRPCMessage], Awaitable[PTOtherServiceRPCMessageResponse]]] = {}


    def __init__(
            self,
            uuid: str = None,
            c2info: [C2ProfileParameters] = None,
            selected_os: str = None,
            commands: CommandList = None,
            wrapped_payload: str = None,
    ):
        self.uuid = uuid
        self.c2info = c2info
        self.selected_os = selected_os
        self.commands = commands
        self.wrapped_payload = wrapped_payload
        if self.agent_path is None:
            self.agent_path = pathlib.Path(".") / self.name
            logger.error(f"{self.name} has no agent_path set, setting to {self.agent_path}")
        if self.agent_code_path is None:
            self.agent_code_path = self.agent_path / "agent_code"
            logger.error(f"{self.name} has no agent_code_path set, setting to {self.agent_code_path}")
        if self.agent_browserscript_path is None:
            self.agent_browserscript_path = self.agent_path / "browser_scripts"

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def file_extension(self):
        pass

    @property
    @abstractmethod
    def author(self):
        pass

    @property
    @abstractmethod
    def supported_os(self):
        pass

    @property
    @abstractmethod
    def wrapper(self):
        pass

    @property
    @abstractmethod
    def wrapped_payloads(self):
        pass

    @property
    @abstractmethod
    def note(self):
        pass

    @property
    @abstractmethod
    def supports_dynamic_loading(self):
        pass

    @property
    @abstractmethod
    def c2_profiles(self):
        pass

    @property
    @abstractmethod
    def build_parameters(self):
        pass

    @abstractmethod
    async def build(self) -> BuildResponse:
        pass

    def get_parameter(self, name):
        for arg in self.build_parameters:
            if arg.name == name:
                return arg.value
        return None

    async def set_and_validate_build_parameters(self, buildinfo: dict):
        # set values for all of the key-value pairs presented to us
        for bp in self.build_parameters:
            if bp.name in buildinfo and buildinfo[bp.name] is not None:
                bp.value = buildinfo[bp.name]
            if bp.required and bp.value is None:
                raise ValueError(
                    "{} is a required parameter but has no value".format(bp.name)
                )

    def get_build_instance_values(self):
        values = {}
        for bp in self.build_parameters:
            if bp.value is not None:
                values[bp.name] = bp.value
        return values

    def to_json(self):
        agent_bytes = self.agent_icon_bytes
        if agent_bytes is None:
            if self.agent_icon_path is not None:
                # read agent icon path
                try:
                    with open(self.agent_icon_path, "rb") as f:
                        agent_bytes = f.read()
                except Exception as e:
                    logger.exception(f"failed to read agent icon from ({self.agent_icon_path}): {e}")
                    agent_bytes = b""
            else:
                logger.error(f"{self.name} has no agent_icon_bytes or agent_icon_path specified, no icon will be used")
                agent_bytes = b""
        return {
            "name": self.name,
            "file_extension": self.file_extension,
            "author": self.author,
            "supported_os": [str(x) for x in self.supported_os],
            "wrapper": self.wrapper,
            "supported_wrapper_payload_types": self.wrapped_payloads,
            "supports_dynamic_load": self.supports_dynamic_loading,
            "description": self.note,
            "build_parameters": [b.to_json() for b in self.build_parameters],
            "supported_c2_profiles": self.c2_profiles,
            "translation_container_name": self.translation_container,
            "mythic_encrypts": self.mythic_encrypts,
            "build_steps": [x.to_json() for x in self.build_steps],
            "agent_icon": base64.b64encode(agent_bytes).decode(),
        }


payloadTypes: dict[str, PayloadType] = {}