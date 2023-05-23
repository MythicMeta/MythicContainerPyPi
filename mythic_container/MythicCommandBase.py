from abc import abstractmethod, ABCMeta
import json
from enum import Enum
import base64
import uuid
from pathlib import Path
from .logging import logger
import sys
from collections.abc import Callable, Awaitable
from mythic_container.MythicGoRPC.send_mythic_rpc_payload_create_from_scratch import \
    MythicRPCPayloadConfigurationBuildParameter, MythicRPCPayloadConfigurationC2Profile


class SupportedOS:
    """Supported Operating System

    This OS value is selected first when generating a payload or wrapper.

    If you don't want to use a listed value, supply your own with
    SupportedOS("my os")
    """
    Windows = "Windows"
    MacOS = "macOS"
    Linux = "Linux"
    Chrome = "Chrome"

    def __init__(self, os: str):
        self.os = os

    def __str__(self):
        return self.os


class MythicStatus:
    Error = "error"
    Completed = "completed"
    Processed = "processed"
    Processing = "processing"
    Preprocessing = "preprocessing"
    Delegating = "delegating subtasks"
    CallbackError = "task callback error"
    Success = "success"

    def __init__(self, status: str):
        self.status = status

    def __str__(self):
        return self.status

    def __eq__(self, obj):
        # check if self.status == obj
        if isinstance(obj, str):
            return self.status == obj
        elif isinstance(obj, MythicStatus):
            return self.status == obj.status
        else:
            return False


class ParameterType(str, Enum):
    """Types of parameters available for Commands

    File type will be a file's UUID in your parse_arguments and create_go_tasking functions.

    Credential_JSON will be a dictionary of credential attributes (account, realm, credential, comment).

    PayloadList will be a list of payloads to the user to select via a dropdown option, but will be passed back as a payload's UUID.

    ConnectionInfo is a dictionary of Payload/C2 information to help make P2P connections easier for an agent.

    LinkInfo is a dictionary of the same information as ConnectionInfo, but presented to the user as a dropdown of choices.
    """
    String = "String"
    Boolean = "Boolean"
    File = "File"
    Array = "Array"
    ChooseOne = "ChooseOne"
    ChooseMultiple = "ChooseMultiple"
    Credential_JSON = "CredentialJson"
    Number = "Number"
    Payload = "PayloadList"
    ConnectionInfo = "AgentConnect"
    LinkInfo = "LinkInfo"


class CommandAttributes:
    """Metadata attributes about a command

    These attributes help determine which commands can be loaded in, which ones are always included, and even free-form attributes the developer wants to track.

    filter_by_build_parameter is of the form {"build param name": "build param value"}

    Attributes:
        supported_os (list[SupportedOS]): Which operating systems does this command support? An empty list means all OS.
        builtin (bool): Is this command baked into the agent permanently?
        suggested_command (bool): If true, this command will appear on the "included" side when building your payload by default.
        load_only (bool): If true, this command can only be loaded after you have a callback and not included in the base payload.
        filter_by_build_parameter (dict): Specify if this command is allowed to be built into the payload or not based on build parameters the user specifies.

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 spawn_and_injectable: bool = False,
                 supported_os: [SupportedOS] = None,
                 builtin: bool = False,
                 suggested_command: bool = False,
                 load_only: bool = False,
                 filter_by_build_parameter: dict = {},
                 **kwargs):
        self.spawn_and_injectable = spawn_and_injectable
        self.supported_os = supported_os
        self.builtin = builtin
        self.suggested_command = suggested_command
        self.load_only = load_only
        self.filter_by_build_parameter = filter_by_build_parameter
        self.additional_items = {}
        for k, v in kwargs.items():
            self.additional_items[k] = v

    def to_json(self):
        r = {}
        if self.spawn_and_injectable is not None:
            r["spawn_and_injectable"] = self.spawn_and_injectable
        else:
            r["spawn_and_injectable"] = False
        if self.supported_os is not None:
            r["supported_os"] = [str(x) for x in self.supported_os]
        else:
            r["supported_os"] = []
        r["builtin"] = self.builtin
        r["suggested_command"] = self.suggested_command
        r["load_only"] = self.load_only
        r["filter_by_build_parameter"] = self.filter_by_build_parameter
        r["additional_items"] = self.additional_items
        return r

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ParameterGroupInfo:
    """Information about a group of parameters for a command.

    ParameterGroups allow conditional parameters displayed to the user.

    Attributes:
        required (bool): In this parameter group, is this parameter required?
        group_name (str): The name of the parameter group? If one isn't provided, the default is `Default`
        ui_position (int): For this parameter group, which order should the parameters appear in the UI?

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(
            self,
            required: bool = True,
            group_name: str = "Default",
            ui_position: int = None,
            **kwargs
    ):
        self.required = required
        self.group_name = group_name
        self.ui_position = ui_position
        self.additional_info = {}
        for k, v in kwargs.items():
            self.additional_info[k] = v

    def to_json(self):
        r = {"required": self.required, "group_name": self.group_name, "ui_position": self.ui_position,
             "additional_info": self.additional_info}
        return r

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTRPCDynamicQueryFunctionMessage:
    """Request to dynamically generate choices for a modal in the UI with a ChooseOne or ChooseMultiple parameter type.

    Attributes:
        Command (str): Name of the command
        ParameterName (str): Name of the parameter
        PayloadType (str): Name of the PayloadType
        Callback (int): ID of the Callback where this function is called. This can be used for PRC calls to Mythic

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 command: str,
                 parameter_name: str,
                 payload_type: str,
                 callback: int):
        self.Command = command
        self.ParameterName = parameter_name
        self.PayloadType = payload_type
        self.Callback = callback

    def to_json(self):
        return {
            "command": self.Command,
            "parameter_name": self.ParameterName,
            "payload_type": self.PayloadType,
            "callback": self.Callback
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTRPCDynamicQueryFunctionMessageResponse:
    """Results of performing a dynamic query for a command

    Attributes:
        Success (bool): Did the dynamic query function successfully execute
        Error (str): If the dynamic query function failed to run, this is the string error
        Choices (list[str]): List of the string choices to present back to the user. If there are no valid choices, return []

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool = False,
                 Error: str = None,
                 Choices: list[str] = []):
        self.Success = Success
        self.Error = Error
        self.Choices = Choices

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "choices": self.Choices
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class CommandParameter:
    """Definition of an argument for a command

    Attributes:
        name (str): Name of the parameter. This is used for get_arg, set_arg, etc functions and used when making the final JSON string to send down to the callback
        type (ParameterType): The type of parameter this is. This determines valid values and how things are presented to the user in the UI.
        display_name (str): More verbose name displayed to the user in the UI
        cli_name (str): More simplified name used when using tab-complete on the command line inside Mythic's UI
        description (str): Description of the argument displayed when the user hovers over the name of the argument.
        choices (list[str]): Choices for the user to select if the type is ChooseOne or ChooseMultiple
        default_value (any): Default value to populate for the user or to select if the user didn't provide anything (such as not using the modal popup).
        supported_agents (list[str]): When using the "Payload" Parameter Type, you can filter down which payloads are presented to the operator based on this list of supported agents.
        supported_agent_build_parameters (dict): When using the "Payload" Parameter Type, you can filter down which payloads are presented to the operator based on specific build parameters for specific payload types.
        choice_filter_by_command_attributes (dict): When using the ChooseOne or ChooseMultiple Parameter type along with choices_are_all_commands, you can filter down those options based on attribute values in your command's CommandAttributes field.
        choices_are_all_commands (bool): Can be used with ChooseOne or ChooseMultiple Parameter Types to automatically populate those options in the UI with all of the commands for the payload type.
        choices_are_loaded_commands (bool): Can be used with ChooseOne or ChooseMultiple Parameter Types to automatically populate those options in the UI with all of the currently loaded commands.
        parameter_group_info (list[ParameterGroupInfo]): Define 0+ different parameter groups that this parameter belongs to.
        dynamic_query_function: Provide a dynamic query function to be called when the user views that parameter option in the UI to populate choices for the ChooseOne or ChooseMultiple Parameter Types.

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(
            self,
            name: str,
            type: ParameterType,
            display_name: str = None,
            cli_name: str = None,
            description: str = "",
            choices: [any] = None,
            default_value: any = None,
            validation_func: callable = None,
            value: any = None,
            supported_agents: [str] = None,
            supported_agent_build_parameters: dict = None,
            choice_filter_by_command_attributes: dict = None,
            choices_are_all_commands: bool = False,
            choices_are_loaded_commands: bool = False,
            dynamic_query_function: Callable[
                [PTRPCDynamicQueryFunctionMessage], Awaitable[PTRPCDynamicQueryFunctionMessageResponse]] = None,
            parameter_group_info: [ParameterGroupInfo] = None
    ):
        self.name = name
        if display_name is None:
            self.display_name = name
        else:
            self.display_name = display_name
        if cli_name is None:
            self.cli_name = name
        else:
            self.cli_name = cli_name
        self.type = type
        self.user_supplied = False  # keep track of if this is using the default value or not
        self.description = description
        if choices is None:
            self.choices = []
        else:
            self.choices = choices
        self.validation_func = validation_func
        if value is None:
            self._value = default_value
        else:
            self.value = value
        self.default_value = default_value
        self.supported_agents = supported_agents if supported_agents is not None else []
        self.supported_agent_build_parameters = supported_agent_build_parameters if supported_agent_build_parameters is not None else {}
        self.choice_filter_by_command_attributes = choice_filter_by_command_attributes if choice_filter_by_command_attributes is not None else {}
        self.choices_are_all_commands = choices_are_all_commands
        self.choices_are_loaded_commands = choices_are_loaded_commands
        self.dynamic_query_function = dynamic_query_function
        if not callable(dynamic_query_function) and dynamic_query_function is not None:
            raise Exception("dynamic_query_function is not callable")
        self.parameter_group_info = parameter_group_info
        if self.parameter_group_info is None:
            self.parameter_group_info = [ParameterGroupInfo()]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, choices):
        self._choices = choices

    @property
    def validation_func(self):
        return self._validation_func

    @validation_func.setter
    def validation_func(self, validation_func):
        self._validation_func = validation_func

    @property
    def supported_agents(self):
        return self._supported_agents

    @supported_agents.setter
    def supported_agents(self, supported_agents):
        self._supported_agents = supported_agents

    @property
    def supported_agent_build_parameters(self):
        return self._supported_agent_build_parameters

    @supported_agent_build_parameters.setter
    def supported_agent_build_parameters(self, supported_agent_build_parameters):
        self._supported_agent_build_parameters = supported_agent_build_parameters

    @property
    def dynamic_query_func(self) -> Callable[
        [PTRPCDynamicQueryFunctionMessage], Awaitable[PTRPCDynamicQueryFunctionMessageResponse]]:
        return self._dynamic_query_func

    @dynamic_query_func.setter
    def dynamic_query_func(self, dynamic_query_func):
        self._dynamic_query_func = dynamic_query_func

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            type_validated = TypeValidators().validate(self.type, value)
            if self.validation_func is not None:
                try:
                    self.validation_func(type_validated)
                    self._value = type_validated
                except Exception as e:
                    raise ValueError(
                        "Failed validation check for parameter {} with value {}".format(
                            self.name, str(value)
                        )
                    )
                self.user_supplied = True
                return
            else:
                # now we do some verification ourselves based on the type
                self._value = type_validated
                self.user_supplied = True
                return
        self._value = value
        self.user_supplied = True
        return

    @property
    def parameter_group_info(self):
        return self._parameter_group_info

    @parameter_group_info.setter
    def parameter_group_info(self, parameter_group_info):
        self._parameter_group_info = parameter_group_info

    def to_json(self):
        return {
            "name": self._name,
            "display_name": self.display_name,
            "cli_name": self.cli_name.replace(" ", "-"),
            "parameter_type": self._type.value,
            "description": self._description,
            "choices": self._choices,
            "default_value": self.default_value,
            "value": self.value,
            "supported_agents": self._supported_agents,
            "supported_agent_build_parameters": self._supported_agent_build_parameters,
            "choices_are_loaded_commands": self.choices_are_loaded_commands,
            "choices_are_all_commands": self.choices_are_all_commands,
            "choice_filter_by_command_attributes": self.choice_filter_by_command_attributes,
            "dynamic_query_function": self.dynamic_query_function.__name__ if callable(
                self.dynamic_query_function) else None,
            "parameter_group_info": [x.to_json() for x in
                                     self.parameter_group_info] if self.parameter_group_info is not None else [
                ParameterGroupInfo().to_json()]
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class TypeValidators:
    def validateString(self, val):
        return str(val)

    def validateNumber(self, val):
        try:
            return int(val)
        except:
            return float(val)

    def validateBoolean(self, val):
        if isinstance(val, bool):
            return val
        else:
            raise ValueError("Value isn't bool")

    def validateFile(self, val):
        try:  # check if the file is actually a file-id
            uuid_obj = uuid.UUID(val, version=4)
            return str(uuid_obj)
        except ValueError:
            pass
        return base64.b64decode(val)

    def validateArray(self, val):
        if isinstance(val, list):
            return val
        else:
            raise ValueError("value isn't array")

    def validateCredentialJSON(self, val):
        if isinstance(val, dict):
            return val
        else:
            raise ValueError("value ins't a dictionary")

    def validatePass(self, val):
        return val

    def validateChooseMultiple(self, val):
        if isinstance(val, list):
            return val
        else:
            raise ValueError("Choices aren't in a list")

    def validatePayloadList(self, val):
        return str(uuid.UUID(val, version=4))

    def validateAgentConnect(self, val):
        if isinstance(val, dict):
            return val
        else:
            raise ValueError("Not instance of dictionary")

    switch = {
        "String": validateString,
        "Number": validateNumber,
        "Boolean": validateBoolean,
        "File": validateFile,
        "Array": validateArray,
        "CredentialJson": validateCredentialJSON,
        "ChooseOne": validatePass,
        "ChooseMultiple": validateChooseMultiple,
        "PayloadList": validatePayloadList,
        "AgentConnect": validateAgentConnect,
        "LinkInfo": validateAgentConnect
    }

    def validate(self, type: ParameterType, val: any):
        return self.switch[type.value](self, val)


class TaskArguments(metaclass=ABCMeta):
    """Definition of how to process a task's arguments (what the user supplied) into the corresponding command's parameters

    Attributes:
        command_line (str):
            The command line (after parsing by the UI if tasked through the UI)
        raw_command_line (str):
            The exact thing the user typed/submitted without any parsing
        tasking_location (str):
            Location of where the task came from (command_line, mythic ui, modal, browser script, etc)
        parameter_group_name (str):
            The name of the parameter group identified for this set of arguments with values
        args (list[CommandParameter]):
            The running/updated set of command parameters supplied with values from the user's tasking


    Functions:
        get_arg:
            Return the value for a certain command parameter (either default value or what the user supplied)
        has_arg:
            Check if a certain command parameter exists
        add_arg:
            Add/update a command parameter with the specified values, types, and parameter groups
        set_arg:
            Set the value for a certain command parameter explicitly
        rename_arg:
            Rename a command parameter's name temporarily
        remove_arg:
            Remove a command parameter temporarily
        set_manual_args:
            Explicitly set the string value that'll be passed down to the callback for this task instead of allowing Mythic to determine the JSON string
        load_args_from_json_string:
            Given a JSON string, parse it into a dictionary and pre-populate command parameters with those values. Any extras are ignored.
        load_args_from_dictionary:
            Given a dictionary, pre-populate command parameters with those values. Any extras are ignored.
        get_parameter_group_name:
            Get the current parameter group name based on all the set command parameter values up to this point
        get_parameter_group_arguments:
            Get all the command parameters that match the current parameter group name
        verify_required_args_have_values:
            Verify that all command parameters for the current parameter group that are required have values
        parse_arguments:
            Parse the string supplied by the user into the appropriate command parameters. Often this is just a call to load_args_from_json_string, but if the user typed free-form arguments, you might need to do additional parsing here on the self.command_line or self.raw_command_line fields.
    """
    manual_args: str = None

    def __init__(self,
                 command_line: str = "",
                 tasking_location: str = "command_line",
                 raw_command_line: str = "",
                 task_dictionary: dict = {},
                 initial_parameter_group: str = ""):
        self.command_line = str(command_line)
        self.tasking_location = tasking_location
        self.raw_command_line = raw_command_line
        self.task_dictionary = task_dictionary
        self.parameter_group_name = None
        self.initial_parameter_group = initial_parameter_group

    @property
    def args(self) -> list[CommandParameter]:
        return self._args

    @args.setter
    def args(self, args):
        self._args = args

    def get_arg(self, key: str):
        for arg in self.args:
            if arg.name == key:
                return arg.value
        return None

    def set_manual_args(self, params: str):
        self.manual_args = params

    def has_arg(self, key: str) -> bool:
        for arg in self.args:
            if arg.name == key:
                return True
        return False

    def get_command_line(self) -> str:
        return self.command_line

    def get_raw_command_line(self) -> str:
        return self.raw_command_line

    def get_tasking_location(self) -> str:
        return self.tasking_location

    def is_empty(self) -> bool:
        return len(self.args) == 0

    def add_arg(self, key: str, value, type: ParameterType = None,
                parameter_group_info: [ParameterGroupInfo] = None):
        found = False
        for arg in self.args:
            if arg.name == key:
                if type is not None:
                    arg.type = type
                if parameter_group_info is not None:
                    arg.parameter_group_info = parameter_group_info
                arg.value = value
                found = True
        if not found:
            newGroupInfo = [ParameterGroupInfo()]
            if parameter_group_info is not None:
                newGroupInfo = parameter_group_info
            if type is not None:
                self.args.append(
                    CommandParameter(name=key, type=type, value=value, parameter_group_info=newGroupInfo))
            else:
                self.args.append(CommandParameter(name=key, type=ParameterType.String, value=value,
                                                  parameter_group_info=newGroupInfo))

    def set_arg(self, key: str, value):
        found = False
        for arg in self.args:
            if arg.name == key:
                arg.value = value
                found = True
        if not found:
            self.add_arg(key, value)

    def rename_arg(self, old_key: str, new_key: str):
        for arg in self.args:
            if arg.name == old_key:
                arg.name = new_key
                return
        raise Exception("{} not a valid parameter name".format(old_key))

    def remove_arg(self, key: str):
        self.args = [x for x in self.args if x.name != key]

    def to_json(self):
        return [x.to_json() for x in self.args]

    def load_args_from_json_string(self, command_line: str) -> None:
        temp_dict = json.loads(command_line)
        for k, v in temp_dict.items():
            for arg in self.args:
                if arg.name == k or arg.cli_name == k:
                    arg.value = v

    def load_args_from_dictionary(self, dictionary) -> None:
        for k, v in dictionary.items():
            for arg in self.args:
                if arg.name == k or arg.cli_name == k:
                    arg.value = v

    def get_parameter_group_name(self) -> str:
        if self.parameter_group_name is not None:
            return self.parameter_group_name
        elif self.manual_args is not None:
            return "Custom"
        groupNameOptions = []
        suppliedArgNames = []
        if len(self.args) == 0:
            return "Default"
        for arg in self.args:
            for group_info in arg.parameter_group_info:
                if group_info.group_name not in groupNameOptions:
                    groupNameOptions.append(group_info.group_name)
        for arg in self.args:
            # when determining the group we're in, only look at arguments that have values that were set by the user
            # default values don't count
            if arg.value is not None and arg.user_supplied:
                suppliedArgNames.append(arg.name)
                groupNameIntersection = []
                for group_info in arg.parameter_group_info:
                    if group_info.group_name in groupNameOptions:
                        groupNameIntersection.append(group_info.group_name)
                groupNameOptions = groupNameIntersection
            # this gives us the groups that our currently supplied commands belong to, but doesn't account for some groups still needing other parameters
            # need to loop through available options and see if we have all of the needed parameters
        if len(groupNameOptions) == 0:
            raise ValueError(f"Supplied Arguments, {suppliedArgNames}, don't match any parameter group")
        elif len(groupNameOptions) > 1:
            finalMatchingGroupNames = []
            for groupNameOption in groupNameOptions:
                has_all_values = True
                for arg in self.args:
                    for group_info in arg.parameter_group_info:
                        if group_info.group_name == groupNameOption:
                            if group_info.required and not arg.user_supplied:
                                # one of our matching parameter groups that we've supplied values for requires this parameter, but the user didn't supply one
                                # so this parameter group can't be the one we use
                                has_all_values = False
                if has_all_values:
                    finalMatchingGroupNames.append(groupNameOption)
            if len(finalMatchingGroupNames) == 0:
                raise ValueError(
                    f"Supplied Arguments, {suppliedArgNames}, match more than one parameter group, {groupNameOptions}, and all require at least one more value from the user")
            elif len(finalMatchingGroupNames) > 1:
                if self.initial_parameter_group in finalMatchingGroupNames:
                    return self.initial_parameter_group
                raise ValueError(
                    f"Supplied Arguments, {suppliedArgNames}, match more than one parameter group, {finalMatchingGroupNames}")
            else:
                return finalMatchingGroupNames[0]
        else:
            return groupNameOptions[0]

    def get_parameter_group_arguments(self) -> [CommandParameter]:
        groupName = self.get_parameter_group_name()
        group_arguments = []
        for arg in self.args:
            matched_arg = False
            for group_info in arg.parameter_group_info:
                if group_info.group_name == groupName:
                    matched_arg = True
            if matched_arg:
                group_arguments.append(arg)
        return group_arguments

    async def verify_required_args_have_values(self) -> bool:
        # first we have to establish which parameter group we're in
        if self.manual_args is not None:
            return True
        groupName = self.get_parameter_group_name()
        for arg in self.args:
            matched_arg = False
            arg_required = False
            for group_info in arg.parameter_group_info:
                if group_info.group_name == groupName:
                    matched_arg = True
                    arg_required = group_info.required
            if matched_arg:
                if arg.value is None:
                    arg.value = arg.default_value
                if arg_required and arg.value is None:
                    raise ValueError("Required arg {} has no value".format(arg.name))
        return True

    async def get_unused_args(self) -> str:
        if len(self.args) > 0:
            caughtException = ""
            try:
                if self.manual_args is not None:
                    groupName = ""
                else:
                    groupName = self.get_parameter_group_name()
            except Exception as e:
                logger.error(f"Failed to get group name for tasking: {e}\n")
                caughtException = f"Failed to get group name for tasking: {e}\n"
                groupName = "N/A"
            temp = {}
            for arg in self.args:
                matched_arg = False
                for group_info in arg.parameter_group_info:
                    if group_info.group_name == groupName:
                        matched_arg = True
                if not matched_arg:
                    if isinstance(arg.value, bytes):
                        temp[arg.name] = base64.b64encode(arg.value).decode()
                    else:
                        temp[arg.name] = arg.value
            return f"The following args aren't being used because they don't belong to the {groupName} parameter group: \n{json.dumps(temp, indent=2)}\n{caughtException}"
        else:
            return ""

    def __str__(self) -> str:
        if self.manual_args is not None:
            if isinstance(self.manual_args, dict):
                return json.dumps(self.manual_args)
            else:
                return str(self.manual_args)
        if len(self.args) > 0:
            try:
                groupName = self.get_parameter_group_name()
            except Exception as e:
                return self.command_line
            temp = {}
            for arg in self.args:
                matched_arg = False
                for group_info in arg.parameter_group_info:
                    if group_info.group_name == groupName:
                        matched_arg = True
                if matched_arg:
                    if isinstance(arg.value, bytes):
                        temp[arg.name] = base64.b64encode(arg.value).decode()
                    elif arg.value is not None:
                        temp[arg.name] = arg.value
                    else:
                        logger.debug(f"Argument {arg.name} has a Null value, not adding it to JSON")
            return json.dumps(temp)
        else:
            return self.command_line

    @abstractmethod
    async def parse_arguments(self) -> None:
        pass


class Callback:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class BrowserScript:
    """Location and author of browser script code for a command's output

    Attributes:
        script_name (str): The name of the javascript file
        author (str): The name (or handle) of the author of the script

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self, script_name: str, author: str = None, for_new_ui: bool = False):
        self.script_name = script_name
        self.author = author

    def to_json(self, base_path: Path):
        try:
            code_file = (
                    base_path
                    / "{}.js".format(self.script_name)
            )
            if code_file.exists():
                code = code_file.read_bytes().decode()
                #code = base64.b64encode(code).decode()
                return {"script": code, "name": self.script_name, "author": self.author}
            elif Path(self.script_name).exists():
                code = Path(self.script_name).read_bytes().decode()
                #code = base64.b64encode(code).decode()
                return {"script": code, "name": self.script_name, "author": self.author}
            else:
                raise Exception(
                    "Code for Browser Script, " + self.script_name + ", does not exist on disk at path: " + str(
                        code_file))
        except Exception as e:
            raise e


class MythicTask:
    """Instance of Mythic Tasking used with `create_tasking`. Use `create_go_tasking` instead.

    Deprecated
    """

    def __init__(
            self,
            taskinfo: dict,
            args: TaskArguments,
            callback_info: dict
    ):
        self.id = taskinfo["id"]
        self.original_params = taskinfo["original_params"]
        self.completed = taskinfo["completed"]
        self.callback = Callback(**callback_info)
        self.agent_task_id = taskinfo["agent_task_id"]
        self.token = taskinfo["token_id"]
        if self.token <= 0:
            self.token = None
        self.operator = taskinfo["operator_username"]
        self.opsec_pre_blocked = taskinfo["opsec_pre_blocked"]
        self.opsec_pre_message = taskinfo["opsec_pre_message"]
        self.opsec_pre_bypassed = taskinfo["opsec_pre_bypassed"]
        self.opsec_pre_bypass_role = taskinfo["opsec_pre_bypass_role"]
        self.opsec_post_blocked = taskinfo["opsec_post_blocked"]
        self.opsec_post_message = taskinfo["opsec_post_message"]
        self.opsec_post_bypassed = taskinfo["opsec_post_bypassed"]
        self.opsec_post_bypass_role = taskinfo["opsec_post_bypass_role"]
        self.display_params = taskinfo["display_params"]
        self.command_name = taskinfo["command_name"]
        self.args = args
        self.manual_args = None
        self.status = MythicStatus.Preprocessing
        if 'status' in taskinfo and taskinfo['status'] is not None:
            self.status = MythicStatus(taskinfo['status'])
        self.tasking_location = taskinfo["tasking_location"] if "tasking_location" in taskinfo else "command_line"
        self.stdout = taskinfo["stdout"] if "stdout" in taskinfo else ""
        self.stderr = taskinfo["stderr"] if "stderr" in taskinfo else ""
        self.subtask_callback_function = taskinfo["subtask_callback_function"]
        self.group_callback_function = taskinfo["group_callback_function"]
        self.completed_callback_function = taskinfo["completed_callback_function"]
        self.subtask_group_name = taskinfo["subtask_group_name"]
        self.parameter_group_name = taskinfo["parameter_group_name"]
        # self.tags is an array of tags to associate with the task

    def get_status(self) -> MythicStatus:
        return self.status

    def set_status(self, status: MythicStatus):
        self.status = status

    def set_stdout(self, stdout: str):
        self.stdout = stdout

    def set_stderr(self, stderr: str):
        self.stderr = stderr

    # if you call override_args with your own values, then we won't use the standard JSON string from self.args
    #   this combined with command_name can allow you to completely set what gets sent to your agent
    def override_args(self, args: str):
        self.manual_args = args

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        subtask_callback_function = self.subtask_callback_function
        if callable(subtask_callback_function):
            subtask_callback_function = subtask_callback_function.__name__
        group_callback_function = self.group_callback_function
        if callable(group_callback_function):
            group_callback_function = group_callback_function.__name__
        completed_callback_function = self.completed_callback_function
        if callable(completed_callback_function):
            completed_callback_function = completed_callback_function.__name__
        command_args = str(self.args)
        if self.manual_args is not None:
            command_args = self.manual_args
        return {
            "args": command_args,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "opsec_pre_blocked": self.opsec_pre_blocked,
            "opsec_pre_message": self.opsec_pre_message,
            "opsec_pre_bypass_role": self.opsec_pre_bypass_role,
            "opsec_pre_bypassed": self.opsec_pre_bypassed,
            "opsec_post_blocked": self.opsec_post_blocked,
            "opsec_post_message": self.opsec_post_message,
            "opsec_post_bypass_role": self.opsec_post_bypass_role,
            "opsec_post_bypassed": self.opsec_post_bypassed,
            "display_params": self.display_params,
            "subtask_callback_function": subtask_callback_function,
            "group_callback_function": group_callback_function,
            "completed_callback_function": completed_callback_function,
            "subtask_group_name": self.subtask_group_name,
            "command_name": self.command_name,
            "parameter_group_name": self.parameter_group_name,
        }


class AgentResponse:
    def __init__(self, response: any, task: MythicTask):
        self.response = response
        self.task = task


class PTTTaskOPSECPreTaskMessageResponse:
    """Result of running an OPSEC check against a task's information before the create_go_tasking function is called

    Attributes:
        TaskID (int): The task this response is referring to
        Success (str): Did the check happen successfully or not
        Error (str): If the check failed to run, this Error provides the message as to why
        OpsecPreBlocked (bool): Is this task blocked from running or not?
        OpsecPreMessage (str): What information do you want to present back to the user as to why it was blocked or not?
        OpsecPreBypassed (bool): Is the block bypassed? You can opt to mark the task as blocked but still allow it through.
        OpsecPreBypassRole (str): If the task is blocked, who is allowed to bypass it? Can be 'operator', 'lead', or 'other_operator'.

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 TaskID: int = None,
                 Success: bool = False,
                 Error: str = "",
                 OpsecPreBlocked: bool = False,
                 OpsecPreMessage: str = "",
                 OpsecPreBypassed: bool = None,
                 OpsecPreBypassRole: str = "operator",
                 **kwargs):
        self.TaskID = TaskID
        self.Success = Success
        self.Error = Error
        self.OpsecPreBlocked = OpsecPreBlocked
        self.OpsecPreMessage = OpsecPreMessage
        self.OpsecPreBypassed = OpsecPreBypassed
        self.OpsecPreBypassRole = OpsecPreBypassRole
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "success": self.Success,
            "error": self.Error,
            "opsec_pre_blocked": self.OpsecPreBlocked,
            "opsec_pre_message": self.OpsecPreMessage,
            "opsec_pre_bypassed": self.OpsecPreBypassed,
            "opsec_pre_bypass_role": self.OpsecPreBypassRole
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTTTaskOPSECPostTaskMessageResponse:
    """Result of running an OPSEC check against a task's information after the create_go_tasking function is called.

    This can be useful in case the create_go_tasking function created additional files that you want to check for OPSEC issues first before allowing an agent to pick up the task.

    Attributes:
        TaskID (int): The task this response is referring to
        Success (str): Did the check happen successfully or not
        Error (str): If the check failed to run, this Error provides the message as to why
        OpsecPostBlocked (bool): Is this task blocked from running or not?
        OpsecPostMessage (str): What information do you want to present back to the user as to why it was blocked or not?
        OpsecPostBypassed (bool): Is the block bypassed? You can opt to mark the task as blocked but still allow it through.
        OpsecPostBypassRole (str): If the task is blocked, who is allowed to bypass it? Can be 'operator', 'lead', or 'other_operator'.

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 TaskID: int = None,
                 Success: bool = False,
                 Error: str = "",
                 OpsecPostBlocked: bool = False,
                 OpsecPostMessage: str = "",
                 OpsecPostBypassed: bool = None,
                 OpsecPostBypassRole: str = "operator",
                 **kwargs):
        self.TaskID = TaskID
        self.Success = Success
        self.Error = Error
        self.OpsecPostBlocked = OpsecPostBlocked
        self.OpsecPostMessage = OpsecPostMessage
        self.OpsecPostBypassed = OpsecPostBypassed
        self.OpsecPostBypassRole = OpsecPostBypassRole
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "success": self.Success,
            "error": self.Error,
            "opsec_post_blocked": self.OpsecPostBlocked,
            "opsec_post_message": self.OpsecPostMessage,
            "opsec_post_bypassed": self.OpsecPostBypassed,
            "opsec_post_bypass_role": self.OpsecPostBypassRole
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTTaskCreateTaskingMessageResponse:
    """Result of running a command's create_go_tasking function.

    Note: If you want to modify the arguments, use taskData.args, not the Params field here.

    Attributes:
        TaskID (int): The task this response is referring to
        Success (str): Did the create_go_tasking function execute properly or was there an error somewhere?
        Error (str): If the create_go_tasking failed to run, this Error provides the message as to why
        CommandName (str): If you want to change the command name that gets sent down to the agent from the name of the current command, change that here. If you don't want to change it, leave it as None.
        TaskStatus (str): If you want to set a specific status (such as 'success', 'completed', or an error status), set that here. If you want things to continue as normal, leave it as None.
        DisplayParams (str): If you want to change what the operator sees displayed in the UI to something else, set that here. This is helpful to get rid of JSON and replace it with something easier to parse for people.
        Stdout (str): If you want to save off some output from the `create_go_tasking` function, but don't want to display it to the user, this is a great way to save that. An example might be build information if you're compiling additional files.
        Stderr (str): If you want to save off some error output from the `create_go_tasking` function, but don't want to display it to the user, this is a great way to save that.
        Completed (bool): If you want to mark this task as "completed" in the UI so that the callback doesn't pick it up, set this to True.
        TokenID (int): If you want to add/change/remove the token id associated with this task, change this value.
        CompletionFunctionName (str): If you want to register a completion function to execute once this task is complete, provide the name here. Your command definition must have a matching dictionary entry with function name to actual function to call.
        ParameterGroupName (str): If you want to override the automatic detection of the parameter group after the creat_go_tasking function executes, set the name here.

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 TaskID: int = None,
                 Success: bool = True,
                 Error: str = "",
                 CommandName: str = None,
                 TaskStatus: str = None,
                 DisplayParams: str = None,
                 Stdout: str = None,
                 Stderr: str = None,
                 Completed: bool = None,
                 TokenID: int = None,
                 CompletionFunctionName: str = None,
                 Params: str = None,
                 ParameterGroupName: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.Success = Success
        self.Error = Error
        self.CommandName = CommandName
        self.TaskStatus = TaskStatus
        self.DisplayParams = DisplayParams
        self.Stdout = Stdout
        self.Stderr = Stderr
        self.Completed = Completed
        self.TokenID = TokenID
        self.CompletionFunctionName = CompletionFunctionName
        self.Params = Params
        self.ParameterGroupName = ParameterGroupName
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "success": self.Success,
            "error": self.Error,
            "command_name": self.CommandName,
            "task_status": self.TaskStatus,
            "display_params": self.DisplayParams,
            "stdout": self.Stdout,
            "stderr": self.Stderr,
            "completed": self.Completed,
            "token_id": self.TokenID,
            "completion_function_name": self.CompletionFunctionName,
            "params": self.Params,
            "parameter_group_name": self.ParameterGroupName
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTTaskMessageTaskData:
    """A container for all information about a task.

    Note: Lowercase names are used in the __init__ function to auto-populate from JSON, but attributes are upper case.

    Attributes:
        ID (int): The unique ID of the task within Mythic, this is used for various RPC calls.
        DisplayID (int): The numerically increasing ID of a task that's shown to the user in the Mythic UI.
        AgentTaskID (str): The UUID of a task that's sent down to a callback.
        CommandName (str): The name of the command to execute within the callback.
        Params (str): A string representation of the parameters that is sent down to the callback.
        Timestamp (str): A string representation of the last time something about the task changed
        CallbackID (int): The unique ID of the callback for this task
        Status (str): The current status of this task (likely to be preprocessing in create_go_tasking)
        OriginalParams (str): The original parameters that the user supplied (after processing by the Mythic UI)
        DisplayParams (str): The modified parameters if any were set to be easier for operators to read (defaults to the same as OriginalParams)
        Comment (str): The comment on the task if one exists
        Stdout (str): Additional stdout for the task if any was set as part of the create_go_tasking function
        Stderr (str): Additional stderr for the task if any was set as part of the create_go_tasking function
        Completed (bool): Indicating if this task is completed or not
        OperatorUsername (str): The name of the operator that issued this task
        OpsecPreBlocked (bool): If this task was originally blocked in the opsec pre check
        OpsecPreMessage (str): A message (if any) provided as part of the opsec pre check
        OpsecPreBypassed (bool): If this task's opsec block was bypassed
        OpsecPreBypassRole (str): Who is able to bypass this opsec block
        OpsecPostBlocked (bool): If the task was blocked in the opsec post check
        OpsecPostMessage (str): A message (if any) provided as part of the ospec post check
        OpsecPostBypassed (bool): If this task's opsec block was bypassed
        OpsecPostBypassRole (str): Who is able to bypass this opsec block
        ParentTaskID (int): If this is a subtask of some other task, this is the ID field for that task
        SubtaskCallbackFunction (str): If this is a subtask and the parent task wants a specific callback function to be executed when this task finishes, the name of that function is here
        SubtaskCallbackFunctionCompleted (bool): Indication of the completion status of that subtask callback function
        GroupCallbackFunction (str): If this is a subtask and part of a group and the parent task wants a specific callback function to be execution when this group of tasks finishes, the name of that function is here
        GroupCallbackFunctionCompleted (bool): Indication of the completion status of that subtask group callback function
        CompletedCallbackFunction (str): If THIS task wants a specific function to execute when it finishes, the name of that function will be here
        CompletedCallbackFunctionCompleted (bool): Indication of the completion status of that callback function
        SubtaskGroupName (str): If this is a subtask and part of a named group, the name of the group will be here
        TaskingLocation (str): The location from where this tasking came (modal, parsed cli, browser script, etc)
        ParameterGroupName (str): The name of the parameter group for this task's command parameters
        TokenID (int): The identifier for the token associated with this task (if one was specified)

    Functions:
        to_json(self): return dictionary form of class
    """
    def __init__(self,
                 id: int = 0,
                 display_id: int = 0,
                 agent_task_id: str = "",
                 command_name: str = "",
                 params: str = "",
                 timestamp: str = "",
                 callback_id: int = 0,
                 status: str = "",
                 original_params: str = "",
                 display_params: str = "",
                 comment: str = "",
                 stdout: str = "",
                 stderr: str = "",
                 completed: bool = False,
                 operator_username: str = "",
                 opsec_pre_blocked: bool = False,
                 opsec_pre_message: str = "",
                 opsec_pre_bypassed: bool = False,
                 opsec_pre_bypass_role: str = "",
                 opsec_post_blocked: bool = False,
                 opsec_post_message: str = "",
                 opsec_post_bypassed: bool = False,
                 opsec_post_bypass_role: str = "",
                 parent_task_id: int = 0,
                 subtask_callback_function: str = "",
                 subtask_callback_function_completed: bool = False,
                 group_callback_function: str = "",
                 group_callback_function_completed: bool = False,
                 completed_callback_function: str = "",
                 completed_callback_function_completed: bool = False,
                 subtask_group_name: str = "",
                 tasking_location: str = "",
                 parameter_group_name: str = "",
                 token_id: int = 0,
                 **kwargs):
        self.ID = id
        self.DisplayID = display_id
        self.AgentTaskID = agent_task_id
        self.CommandName = command_name
        self.Params = params
        self.Timestamp = timestamp
        self.CallbackID = callback_id
        self.Status = status
        self.OriginalParams = original_params
        self.DisplayParams = display_params
        self.Comment = comment
        self.Stdout = stdout
        self.Stderr = stderr
        self.Completed = completed
        self.OperatorUsername = operator_username
        self.OpsecPreBlocked = opsec_pre_blocked
        self.OpsecPreMessage = opsec_pre_message
        self.OpsecPreBypassed = opsec_pre_bypassed
        self.OpsecPreBypassRole = opsec_pre_bypass_role
        self.OpsecPostBlocked = opsec_post_blocked
        self.OpsecPostMessage = opsec_post_message
        self.OpsecPostBypassed = opsec_post_bypassed
        self.OpsecPostBypassRole = opsec_post_bypass_role
        self.ParentTaskID = parent_task_id
        self.SubtaskCallbackFunction = subtask_callback_function
        self.SubtaskCallbackFunctionCompleted = subtask_callback_function_completed
        self.GroupCallbackFunction = group_callback_function
        self.GroupCallbackFunctionCompleted = group_callback_function_completed
        self.CompletedCallbackFunction = completed_callback_function
        self.CompletedCallbackFunctionCompleted = completed_callback_function_completed
        self.SubtaskGroupName = subtask_group_name
        self.TaskingLocation = tasking_location
        self.ParameterGroupName = parameter_group_name
        self.TokenID = token_id

    def to_json(self):
        return {
            "id": self.ID,
            "display_id": self.DisplayID,
            "agent_task_id": self.AgentTaskID,
            "command_name": self.CommandName,
            "params": self.Params,
            "timestamp": self.Timestamp,
            "callback_id": self.CallbackID,
            "status": self.Status,
            "original_params": self.OriginalParams,
            "display_params": self.DisplayParams,
            "comment": self.Comment,
            "stdout": self.Stdout,
            "stderr": self.Stderr,
            "completed": self.Completed,
            "operator_username": self.OperatorUsername,
            "opsec_pre_blocked": self.OpsecPreBlocked,
            "opsec_pre_message": self.OpsecPreMessage,
            "opsec_pre_bypass_role": self.OpsecPreBypassRole,
            "opsec_pre_bypassed": self.OpsecPreBypassed,
            "opsec_post_blocked": self.OpsecPostBlocked,
            "opsec_post_message": self.OpsecPostMessage,
            "opsec_post_bypass_role": self.OpsecPostBypassRole,
            "opsec_post_bypassed": self.OpsecPostBypassed,
            "parent_task_id": self.ParentTaskID,
            "subtask_callback_function": self.SubtaskCallbackFunction,
            "subtask_callback_function_completed": self.SubtaskCallbackFunctionCompleted,
            "group_callback_function": self.GroupCallbackFunction,
            "group_callback_function_completed": self.GroupCallbackFunctionCompleted,
            "completed_callback_function": self.CompletedCallbackFunction,
            "completed_callback_function_completed": self.CompletedCallbackFunctionCompleted,
            "subtask_group_name": self.SubtaskGroupName,
            "tasking_location": self.TaskingLocation,
            "parameter_group_name": self.ParameterGroupName,
            "token_id": self.TokenID,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTTaskMessageCallbackData:
    """A container for all information about a callback.

    Note: Lowercase names are used in the __init__ function to auto-populate from JSON, but attributes are upper case.

    Attributes:
        ID (int): The unique ID of the callback within Mythic, this is used for various RPC calls.
        DisplayID (int): The numerically increasing ID of a callback that's shown to the user in the Mythic UI.
        AgentCallbackID (str): The UUID of a callback that's sent down to a callback.
        InitCallback (str): The time of the initial callback
        LastCheckin (str): The time of the last time the callback checked in
        User (str): The user associated with the callback
        Host (str): The hostname for the callback (always in all caps)
        PID (int): The PID of the callback
        IP (str): The string representation of the IP array for the callback
        IPs (list[str]): An array of the IPs for the callback
        ExternalIp (str): The external IP address (if identified) for the callback
        ProcessName (str): The name of the process for the callback
        Description (str): The description for the callback (by default it matches the description for the associated payload)
        OperatorID (int): The ID of the operator that created the associated payload
        Active (bool): Indicating if this callback is in the active callbacks table or not
        IntegrityLevel (int): The integrity level for the callback that mirrors that of Windows (0-4) with a value of 3+ indicating a High Integrity (or root) callback
        Locked (bool): Indicating if this callback is locked or not so that other operators can't task it
        OperationID (int): The ID of the operation this callback belongs to
        CryptoType (str): The type of cryptography used for this callback (typically None or aes256_hmac)
        DecKey (bytes): The decryption key for this callback
        EncKey (bytes): The encryption key for this callback
        OS (str): The OS information reported back by the callback (not the same as the payload os you selected when building the agent)
        Architecture (str): The architecture of the process where this callback is executing
        Domain (str): The domain associated with the callback if there is one
        ExtraInfo (str): Freeform field of extra data that can be stored and retrieved with a callback
        SleepInfo (str): Freeform sleep information that can be stored and retrieved as part of a callback (this isn't pre-populated, the agent or command files must set it)

    Functions:
        to_json(self): return dictionary form of class
    """
    def __init__(self,
                 id: int = 0,
                 display_id: int = 0,
                 agent_callback_id: str = "",
                 init_callback: str = "",
                 last_checkin: str = "",
                 user: str = "",
                 host: str = "",
                 pid: int = 0,
                 ip: str = "",
                 ips: list[str] = [],
                 external_ip: str = "",
                 process_name: str = "",
                 description: str = "",
                 operator_id: int = 0,
                 active: bool = False,
                 integrity_level: int = 0,
                 locked: bool = False,
                 operation_id: int = 0,
                 crypto_type: str = "",
                 os: str = "",
                 architecture: str = "",
                 domain: str = "",
                 extra_info: str = "",
                 sleep_info: str = "",
                 dec_key: str = None,
                 enc_key: str = None,
                 registered_payload_id: int = 0,
                 **kwargs):
        self.ID = id
        self.DisplayID = display_id
        self.AgentCallbackID = agent_callback_id
        self.InitCallback = init_callback
        self.LastCheckin = last_checkin
        self.User = user
        self.Host = host
        self.PID = pid
        self.IP = ip
        self.IPs = ips
        self.ExternalIp = external_ip
        self.ProcessName = process_name
        self.Description = description
        self.OperatorID = operator_id
        self.Active = active
        self.IntegrityLevel = integrity_level
        self.Locked = locked
        self.OperationID = operation_id
        self.CryptoType = crypto_type
        self.DecKey = base64.b64decode(dec_key) if dec_key is not None else None
        self.EncKey = base64.b64decode(enc_key) if enc_key is not None else None
        self.OS = os
        self.Architecture = architecture
        self.Domain = domain
        self.ExtraInfo = extra_info
        self.SleepInfo = sleep_info
        self.RegisteredPayloadID = registered_payload_id
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "id": self.ID,
            "display_id": self.DisplayID,
            "agent_callback_id": self.AgentCallbackID,
            "init_callback": self.InitCallback,
            "last_checkin": self.LastCheckin,
            "user": self.User,
            "host": self.Host,
            "pid": self.PID,
            "ip": self.IP,
            "ips": self.IPs,
            "external_ip": self.ExternalIp,
            "process_name": self.ProcessName,
            "description": self.Description,
            "operator_id": self.OperatorID,
            "active": self.Active,
            "integrity_level": self.IntegrityLevel,
            "locked": self.Locked,
            "operation_id": self.OperationID,
            "crypto_type": self.CryptoType,
            "dec_key": self.DecKey,
            "enc_key": self.EncKey,
            "os": self.Os,
            "architecture": self.Architecture,
            "domain": self.Domain,
            "extra_info": self.ExtraInfo,
            "sleep_info": self.SleepInfo
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTTaskMessagePayloadData:
    """A container for basic information about the payload associated with a task.

    Note: Lowercase names are used in the __init__ function to auto-populate from JSON, but attributes are upper case.

    Attributes:
        OS (str): The operating system selected as the first step in generating this payload
        UUID (str): The UUID for the payload
        PayloadType (str): The name of the payload type associated with this payload

    Functions:
        to_json(self): return dictionary form of class
    """
    def __init__(self,
                 os: str = "",
                 uuid: str = "",
                 payload_type: str = "",
                 **kwargs):
        self.OS = os
        self.UUID = uuid
        self.PayloadType = payload_type
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "os": self.OS,
            "uuid": self.UUID,
            "payload_type": self.PayloadType
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTTaskMessageAllData:
    """A container for all information about a Task including the task, callback, build parameters, commands, etc.

    Note: Lowercase names are used in the __init__ function to auto-populate from JSON, but attributes are upper case.

    Attributes:
        Task (PTTaskMessageTaskData): The information about this task
        Callback (PTTaskMessageCallbackData): The information about this task's callback
        Payload (PTTaskMessagePayloadData): The information about this task's associated payload
        Commands (list[str]): The names of all the commands currently loaded into this callback
        PayloadType (str): The name of the payload type
        BuildParameters (list[MythicRPCPayloadConfigurationBuildParameter]): Information about the build parameters used to generate the payload for this callback
        C2Profiles (list[MythicRPCPayloadConfigurationC2Profile]): Information about the c2 profiles associated with this callback and their values
        args: The running instance of arguments for this task, this allows you to modify any arguments as necessary in your `create_go_tasking` function

    Functions:
        to_json(self): return dictionary form of class
    """
    args: TaskArguments

    def __init__(self,
                 task: dict = {},
                 callback: dict = {},
                 build_parameters: list[dict] = [],
                 commands: list[str] = [],
                 payload: dict = {},
                 c2info: list[dict] = [],
                 payload_type: str = "",
                 args: TaskArguments.__class__ = None,
                 **kwargs):
        self.Task = PTTaskMessageTaskData(**task)
        self.Callback = PTTaskMessageCallbackData(**callback)
        self.Payload = PTTaskMessagePayloadData(**payload)
        self.Commands = commands
        self.PayloadType = payload_type
        self.BuildParameters = [MythicRPCPayloadConfigurationBuildParameter(**x) for x in build_parameters]
        self.C2Profiles = [MythicRPCPayloadConfigurationC2Profile(**x) for x in c2info]
        if args is not None:
            self.args = args(command_line=task["params"],
                             tasking_location=task["tasking_location"],
                             raw_command_line=task["original_params"],
                             task_dictionary=task,
                             initial_parameter_group=task["parameter_group_name"])
        else:
            self.args = args
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "task": self.Task.to_json(),
            "callback": self.Callback.to_json(),
            "build_parameters": [x.to_json() for x in self.BuildParameters],
            "commands": self.Commands,
            "payload": self.Payload.to_json(),
            "c2info": [x.to_json() for x in self.C2Profiles],
            "payload_type": self.PayloadType
        }

    def set_args(self, args: TaskArguments.__class__) -> None:
        self.args = args(command_line=self.Task.Params,
                         tasking_location=self.Task.TaskingLocation,
                         raw_command_line=self.Task.OriginalParams, )

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTTaskCompletionFunctionMessage:
    """A request to execute the completion function for a task or subtask

    Note: Lowercase names are used in the __init__ function to auto-populate from JSON, but attributes are upper case.

    Attributes:
        TaskData (PTTaskMessageAllData): Information about this task and its callback, payload, build params, etc
        CompletionFunctionName (str): The name of the completion function to execute
        SubtaskGroup (str): If this task is part of a subtask group, this is the name of that group
        SubtaskData (PTTaskMessageAllData): If this is a completion function from a subtask, then this is all the information about that subtask, not the current task.

    Functions:
        to_json(self): return dictionary form of class
    """
    SubtaskData: PTTaskMessageAllData

    def __init__(self,
                 args: TaskArguments,
                 task: dict,
                 function_name: str,
                 subtask: dict = None,
                 subtask_group_name: str = None,
                 **kwargs):
        self.TaskData = PTTaskMessageAllData(**task, args=args)
        self.CompletionFunctionName = function_name
        self.SubtaskGroup = subtask_group_name
        if subtask is not None:
            self.SubtaskData = PTTaskMessageAllData(**subtask)
        else:
            self.SubtaskData = None
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "task": self.TaskData.to_json(),
            "function_name": self.CompletionFunctionName,
            "subtask": self.SubtaskData.to_json() if self.SubtaskData is not None else None,
            "subtask_group_name": self.SubtaskGroup
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTTaskCompletionFunctionMessageResponse:
    """The result of executing the completion function for a task or subtask

    Attributes:
        TaskID (int): The ID of the task (auto filled in for you)
        ParentTaskId (int): The ID of the parent task (auto filled in for you)
        Success (bool): Did the completion function execute successfully or not
        Error (str): If the completion function failed to execute, return an error message here
        TaskStatus (str): If you want to update the status of the task to something other than default as a result of this execution, set the value here
        DisplayParams (str): If you want to update the display parameters of the task, update them here
        Stdout (str): If you want to save some output about the completion function without adding it to the normal output, save it here
        Stderr (str): If you want to save some stderr about the completion function without adding it to the normal output, save it here
        Completed (bool): If you want to mark the task as completed (so that the agent can't pick it up), set this to True. This is really only useful if this is a function executed as the result of a subtask completing, so you can prevent the callback from getting this task.
        TokenID (int): If you want to add/update/remove the token id associated with this task, set that value here
        CompletionFunctionName (str): If you want to set a completion function for this task, set the name here. Make sure it matches a corresponding entry in your command's definition.
        Params (str): The task parameters that were sent down to the callback as part of the tasking
        ParameterGroupName (str): The name of the parameter group associated with the arguments that were sent down to the callback

    Functions:
        to_json(self): return dictionary form of class
    """
    def __init__(self,
                 TaskID: int = 0,
                 ParentTaskId: int = 0,
                 Success: bool = True,
                 Error: str = None,
                 TaskStatus: str = None,
                 DisplayParams: str = None,
                 Stdout: str = None,
                 Stderr: str = None,
                 Completed: bool = None,
                 TokenID: int = None,
                 CompletionFunctionName: str = None,
                 Params: str = None,
                 ParameterGroupName: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.ParentTaskId = ParentTaskId
        self.Success = Success
        self.Error = Error
        self.TaskStatus = TaskStatus
        self.DisplayParams = DisplayParams
        self.Stdout = Stdout
        self.Stderr = Stderr
        self.Completed = Completed
        self.TokenID = TokenID
        self.CompletionFunctionName = CompletionFunctionName
        self.Params = Params
        self.ParameterGroupName = ParameterGroupName
        for k, v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "parent_task_id": self.ParentTaskId,
            "success": self.Success,
            "error": self.Error,
            "task_status": self.TaskStatus,
            "display_params": self.DisplayParams,
            "stdout": self.Stdout,
            "stderr": self.Stderr,
            "completed": self.Completed,
            "token_id": self.TokenID,
            "completion_function_name": self.CompletionFunctionName,
            "params": self.Params,
            "parameter_group_name": self.ParameterGroupName
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class PTTaskProcessResponseMessageResponse:
    """The result of executing the process response function for a task

    Attributes:
        TaskID (int): The ID of the task
        Success (bool): Did the function execute successfully or not
        Error (str): If the function failed to execute, return an error message here


    Functions:
        to_json(self): return dictionary form of class
    """
    def __init__(self,
                 TaskID: int,
                 Success: bool = True,
                 Error: str = ""):
        self.TaskID = TaskID
        self.Success = Success
        self.Error = Error

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "success": self.Success,
            "error": self.Error
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class CommandBase(metaclass=ABCMeta):
    """The base definition for a command that Mythic tracks for a Payload Type

    Attributes:
        cmd (str): The name of the command
        needs_admin (bool): Indicating if the command needs elevated permissions to execute properly
        help_cmd (str): A short help string for how to run the command
        description (str): Description of what the command does and how it works
        version (int): The current version of the command
        author (str): The name or handle of the author of the command
        attackmapping (list[str]): A list of MITRE ATT&CK Technique IDs (ex: T1033)
        supported_ui_features (list[str]): A list of supported ui features (ex: "callback_table:exit")
        browser_script (BrowserScript): An instance of BrowserScript if the command provides a browser script to manipluate its output
        script_only (bool): Indicate if the command is only a script or if there's backing code within the agent
        attributes (CommandAttributes): Additional attributes about the command such as if it's builtin, suggested, or anything else
        completion_functions (dict): A list of completion/subtask functions by their name and function value so they can be called later
        argument_class (TaskArguments.__class__): The class that's used to parse the future task's arguments into the command's parameters
        agent_code_path (Path): The Path to the code for the agent (helpful for building and loading commands dynamically)
        agent_browserscript_path (Path): The Path to where browser scripts are located for your payload type

    Functions:
        to_json:
            return dictionary form of class
        opsec_pre:
            A function for checking for OPSEC issues before the command is executed
        opsec_post:
            A function for checking for OPSEC issues before a command is executed, but after the create_go_tasking function is executed
        create_go_tasking:
            The main function for doing additional processing of the task before it's ready for the agent to fetch it
        process_response:
            Optional additional processing of responses from the agent in any free-form format

    """
    supported_ui_features: list[str] = []
    browser_script: BrowserScript = None
    script_only: bool = False
    attributes: CommandAttributes = None
    completion_functions: dict[
        str, Callable[[PTTaskCompletionFunctionMessage], Awaitable[PTTaskCompletionFunctionMessageResponse]]] = {}
    argument_class: TaskArguments.__class__
    base_path: Path = Path(".")
    agent_code_path: Path = base_path / "agent_code"
    agent_browserscript_path: Path = base_path / "browser_scripts"

    def __init__(self, agent_path: Path, agent_code_path: Path, agent_browserscript_path: Path):
        self.base_path = agent_path
        self.agent_code_path = agent_code_path
        self.agent_browserscript_path = agent_browserscript_path

    @property
    @abstractmethod
    def cmd(self):
        pass

    @property
    @abstractmethod
    def needs_admin(self):
        pass

    @property
    @abstractmethod
    def help_cmd(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def version(self):
        pass

    @property
    @abstractmethod
    def author(self):
        pass

    @property
    @abstractmethod
    def attackmapping(self):
        pass

    async def opsec_pre(self, taskData: PTTaskMessageAllData) -> PTTTaskOPSECPreTaskMessageResponse:
        response = PTTTaskOPSECPreTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=False,
            OpsecPreMessage="Not implemented, passing by default",
        )
        return response

    async def opsec_post(self, taskData: PTTaskMessageAllData) -> PTTTaskOPSECPostTaskMessageResponse:
        response = PTTTaskOPSECPostTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPostBlocked=False,
            OpsecPostMessage="Not implemented, passing by default",
        )
        return response

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        pass

    def to_json(self):
        params = self.argument_class("").to_json()
        if self.browser_script is not None:
            if isinstance(self.browser_script, list):
                logger.error(f"{self.cmd}'s browserscript attribute should not be an array, but a single script")
                sys.exit(1)
            else:
                try:
                    bscript = {"browserscript": self.browser_script.to_json(self.agent_browserscript_path)}
                except Exception as e:
                    logger.error(f"Failed to get browser script for {self.cmd}:\n{e}")
                    bscript = {}
        else:
            bscript = {"browser_script": {}}
        if self.attributes is None:
            attributes = CommandAttributes()
        else:
            attributes = self.attributes
        return {
            "name": self.cmd,
            "needs_admin_permission": self.needs_admin,
            "help_string": self.help_cmd,
            "description": self.description,
            "version": self.version,
            "supported_ui_features": self.supported_ui_features if self.supported_ui_features is not None else [],
            "author": self.author,
            "attack": self.attackmapping,
            "parameters": params,
            "attributes": attributes.to_json(),
            "script_only": self.script_only if self.script_only is not None else False,
            **bscript,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


commands: dict[str, list[CommandBase]] = {}
