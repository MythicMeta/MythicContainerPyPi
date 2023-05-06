from enum import Enum
from abc import abstractmethod
import base64
from .logging import logger
import json
from collections.abc import Callable, Awaitable
import pathlib


class BuildStatus:
    """Build Status

    This can either be BuildStatus.Success or BuildStatus.Error

    Attributes:
        Success (str): Successful build
        Error (str): Failed build
    """
    Success = "success"
    Error = "error"


class SupportedOS:
    """Supported Operating System

    This OS value is selected first when generating a payload or wrapper.

    If you don't want to use a listed value, supply your own with
    SupportedOS("my os")
    """
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
    """Types of parameters available for building payloads

    Attributes:
        String:
            A string value
        ChooseOne:
            A list of choices for the user to select exactly one
        Array:
            The user can supply multiple values in an Array format
        Date:
            The user can select a Date in YYYY-MM-DD format
        Dictionary:
            The user can supply a dictionary of values
        Boolean:
            The user can toggle a switch for True/False
        File:
            The user can select a file that gets uploaded - a file UUID gets passed in during build
    """
    String = "String"
    ChooseOne = "ChooseOne"
    Array = "Array"
    Date = "Date"
    Dictionary = "Dictionary"
    Boolean = "Boolean"
    File = "File"


class DictionaryChoice:
    """A single dictionary choice/option for the UI when select C2 Profile Parameters

    Attributes:
        name (str): Name of the choice
        default_show (bool): Should this be pre-selected with a default value
        default_value (str): Default value to fill in

    """
    def __init__(self,
                 name: str,
                 default_value: str = "",
                 default_show: bool = True):
        self.name = name
        self.default_show = default_show
        self.default_value = default_value

    def to_json(self):
        return {
            "name": self.name,
            "default_value": self.default_value,
            "default_show": self.default_show
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class BuildParameter:
    """Build Parameter Definition for use when generating payloads

    Attributes:
        name (str):
            Name of the parameter for scripting and for when building payloads
        description (str):
            Informative description displayed when building a payload
        default_value (any):
            Default value to pre-populate
        randomize (bool):
            Should this value be randomized (requires format_string)
        format_string (str):
            A regex used for randomizing values if randomize is true
        parameter_type (BuildParameterType):
            The type of parameter this is
        required (bool):
            Is this parameter required to have a non-empty value or not
        verifier_regex (str):
            Regex used to verify that the user typed something appropriate
        choices (list[str]):
            Choices for ChooseOne parameter type
        dictionary_choices (list[DictionaryChoice]):
            Configuration options for the Dictionary parameter type
        crypto_type (bool):
            Indicate if this value should be used to generate a crypto key or not

    """
    def __init__(
            self,
            name: str,
            parameter_type: BuildParameterType = None,
            description: str = None,
            required: bool = None,
            randomize: bool = None,
            format_string: str = "",
            crypto_type: bool = False,
            verifier_regex: str = None,
            default_value: any = None,
            choices: list[str] = None,
            dictionary_choices: list[DictionaryChoice] = None,
            value: any = None,
            verifier_func: callable = None,
    ):
        self.name = name
        self.verifier_func = verifier_func
        self.parameter_type = (
            parameter_type if parameter_type is not None else BuildParameterType.String
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
        self.dictionary_choices = dictionary_choices
        self.crypto_type = crypto_type
        self.randomize = randomize
        self.format_string = format_string

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "default_value": self.default_value,
            "randomize": self.randomize,
            "format_string": self.format_string,
            "required": self.required,
            "parameter_type": self.parameter_type.value,
            "verifier_regex": self.verifier_regex,
            "crypto_type": self.crypto_type,
            "choices": self.choices,
            "dictionary_choices": [x.to_json() for x in
                                   self.dictionary_choices] if self.dictionary_choices is not None else None
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2ProfileParameters:
    """C2 Profile information for building a payload

    Functions:
        get_c2profile:
            Get a dictionary with metadata about the c2 profile (name, is_p2p)
        get_parameters_dict:
            Get a dictionary of the parameters for the profile
    """
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
    """List of commands that the user wants to build into an agent

    This might include script_only commands that are available in the UI but not actual commands with files for your agent.

    Attributes:
        commands (list[str]):
            The names of the commands

   Functions:
       get_commands:
           Get a list of the command names
   """
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
    """The result of attempting to build a payload

    Attributes:
        status (BuildStatus):
            The status of the build
        payload (bytes):
            The final payload bytes to send back to Mythic if any
        build_message (str):
            A build message to show to the user
        build_stderr (str):
            Any stderr messages you want to save as part of the build process (also shown to the user in case of error)
        build_stdout (str):
            Any stdout data you want to save as part of the build process
        updated_command_list (list[str]):
            An updated list of commands that are actually being built into the payload. This is handy if the user selected commandA but you aren't building it into the payload for some reason. Similarly, it's helpful if the user selected commandA but you also need commandB for that to work, so you can reflect that change back to Mythic.
        updated_filename (str):
            An updated filename - this is useful if the user selects an option during build that changes the file type (ex: exe, dll, zip) and you want to reflect that back in the filename for easier downloading.
   Functions:
       get_commands:
           Get a list of the command names
   """
    def __init__(self, status: BuildStatus, payload: bytes = None, build_message: str = None, build_stderr: str = None,
                 build_stdout: str = None, updated_command_list: [str] = None, updated_filename: str = None):
        self.status = status
        self.payload = payload if payload is not None else b""
        self.build_message = build_message if build_message is not None else ""
        self.build_stderr = build_stderr if build_stderr is not None else ""
        self.build_stdout = build_stdout if build_stdout is not None else ""
        self.updated_command_list = updated_command_list
        self.updated_filename = updated_filename

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

    def get_updated_filename(self):
        return self.updated_filename

    def set_updated_filename(self, filename: str):
        self.updated_filename = filename


class BuildStep:
    """A tracked step in the build process for a payload type

    Attributes:
        step_name (str):
            The name of the step to display to users
        step_description (str):
            The description of the step to display to users

   """
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

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTOtherServiceRPCMessage:
    """Request to call an RPC function of another C2 Profile or Payload Type

    Attributes:
        ServiceName (str): Name of the C2 Profile or Payload Type
        ServiceRPCFunction (str): Name of the function to call
        ServiceRPCFunctionArguments (dict): Arguments to that function

    Functions:
        to_json(self): return dictionary form of class
    """
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

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTOtherServiceRPCMessageResponse:
    """Result of running an RPC call from another service

    Attributes:
        Success (bool): Did the RPC succeed or fail
        Error (str): Error message if the RPC check failed
        Result (dict): Result from the RPC

    Functions:
        to_json(self): return dictionary form of class
    """

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

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PayloadType:
    """Payload Type to import and sync with Mythic

    Attributes:
        name (str):
            Name of the payload type
        file_extension (str):
            Default file extension to apply to payloads
        author (str):
            Author of the Payload Type
        supported_os (list[SupportedOS]):
            List of Operating Systems that this Payload Type supports
        wrapper (bool):
            Is this payload type a wrapper (i.e. it takes in other payload types and wraps them up in a new format)
        wrapped_payloads (list[str]):
            What wrappers does this payload type support (ex: service_wrapper)
        note (str):
            A description of the payload type to present to users
        supports_dynamic_loading (bool):
            Does this payload type support dynamically choosing which commands to build in or not. If this is `False` then when building a payload for this payload type, you won't get the option to pick which commands to add to the payload - they'll all automatically get added.
        c2_profiles (list[str]):
            List of C2 Profile names that this Payload Type supports
        build_parameters (list[BuildParameter]):
            List of build parameters for this Payload Type that the user can modify when building the payload

        uuid (str):
            UUID of the payload
        filename (str):
            The original filename of the payload that the user selected
        c2info (list[C2ProfileParameters]):
            List of C2 Profiles that the user selected to build into the agent along with their parameter values
        commands (CommandList):
            List of commands the user selected to build into the agent
        wrapped_payload (str):
            If this is a wrapper payload type, this is the UUID of the payload to wrap
        selected_os (str):
            The OS the user selected for the first step when building this payload
        build_steps (list[BuildStep]):
            A list of build steps that will be taken during the build process. As you build, you can report back the status of each step so that the user knows what's going on.
        agent_icon_path (str):
            Path to the agent icon you want to use with Mythic. This MUST be a .svg file.
        agent_icon_bytes (bytes):
            If you don't want to provide the path, you can optionally provide the raw bytes to the .svg file here.
        translation_container (str):
            If your payload type uses a translation container, provide the name of it here
        mythic_encrypts (bool):
            Indicate if Mythic should handle encryption/decryption for you or if you want a translation container to do it instead. This is often useful if you want to have a separate form of encryption than what Mythic provides.
        agent_path (Path):
            The path to your agent's main folder. This is used to help determine paths to your code and browser scripts if they aren't provided
        agent_code_path (Path):
            The path to your agent's actual source code
        agent_browserscript_path (Path):
            The path to the folder holding your browser scripts so that they can be fetched when Syncing
        custom_rpc_functions (dict):
            Dictionary of RPC name to awaitable RPC function that other services can call

    Functions:
        build(self):
            Given an instance of a bare payload and all the configuration options that the user selected (build parameters, c2 profile parameters), build the payload
        get_parameter:
            Get the value of a build parameter
    """
    uuid: str = None
    c2info: [C2ProfileParameters] = None
    commands: CommandList = None
    wrapped_payload: str = None
    selected_os: str = None
    filename: str = None
    build_steps = []
    agent_icon_path: str = None
    agent_icon_bytes: bytes = None
    translation_container = None
    mythic_encrypts = True
    agent_path = None
    agent_code_path = None
    agent_browserscript_path = None
    custom_rpc_functions: dict[
        str, Callable[[PTOtherServiceRPCMessage], Awaitable[PTOtherServiceRPCMessageResponse]]] = {}

    def __init__(
            self,
            uuid: str = None,
            filename: str = "",
            c2info: [C2ProfileParameters] = None,
            selected_os: str = None,
            commands: CommandList = None,
            wrapped_payload: str = None,
    ):
        self.uuid = uuid
        self.c2info = c2info
        self.selected_os = selected_os
        self.commands = commands
        self.filename = filename
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

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)

payloadTypes: dict[str, PayloadType] = {}
