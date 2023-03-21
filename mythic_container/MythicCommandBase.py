from abc import abstractmethod, ABCMeta
import json
from enum import Enum
import base64
import uuid
from pathlib import Path
from .logging import logger
import sys
from collections.abc import Callable, Awaitable
from mythic_container.MythicGoRPC.send_mythic_rpc_payload_create_from_scratch import MythicRPCPayloadConfigurationBuildParameter, MythicRPCPayloadConfigurationC2Profile

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
        r = {**r, **self.additional_items}
        return r


class ParameterGroupInfo:
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
        r = {}
        r["required"] = self.required
        r["group_name"] = self.group_name
        r["ui_position"] = self.ui_position
        r = {**r, **self.additional_info}
        return r

class PTRPCDynamicQueryFunctionMessage:
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
class PTRPCDynamicQueryFunctionMessageResponse:
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
class CommandParameter:
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
            dynamic_query_function: Callable[[PTRPCDynamicQueryFunctionMessage], Awaitable[PTRPCDynamicQueryFunctionMessageResponse]] = None,
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
    def dynamic_query_func(self) -> Callable[[PTRPCDynamicQueryFunctionMessage], Awaitable[PTRPCDynamicQueryFunctionMessageResponse]]:
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
        "Credential-JSON": validateCredentialJSON,
        "ChooseOne": validatePass,
        "ChooseMultiple": validateChooseMultiple,
        "PayloadList": validatePayloadList,
        "AgentConnect": validateAgentConnect,
        "LinkInfo": validateAgentConnect
    }

    def validate(self, type: ParameterType, val: any):
        return self.switch[type.value](self, val)


class TaskArguments(metaclass=ABCMeta):
    manual_args: str = None

    def __init__(self,
                 command_line: str = "",
                 tasking_location: str = "command_line",
                 raw_command_line: str = "",
                 task_dictionary: dict = {}):
        self.command_line = str(command_line)
        self.tasking_location = tasking_location
        self.raw_command_line = raw_command_line
        self.task_dictionary = task_dictionary
        self.parameter_group_name = None

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
                    else:
                        temp[arg.name] = arg.value
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
    # if a browserscript is specified as part of a PayloadType, then it's a support script
    # if a browserscript is specified as part of a command, then it's for that command
    def __init__(self, script_name: str, author: str = None, for_new_ui: bool = False):
        self.script_name = script_name
        self.author = author
        self.for_new_ui = for_new_ui

    def to_json(self, base_path: Path):
        try:
            code_file = (
                    base_path
                    / "{}.js".format(self.script_name)
            )
            if code_file.exists():
                code = code_file.read_bytes()
                code = base64.b64encode(code).decode()
                return {"script": code, "name": self.script_name, "author": self.author, "for_new_ui": self.for_new_ui}
            elif Path(self.script_name).exists():
                code = Path(self.script_name).read_bytes()
                code = base64.b64encode(code).decode()
                return {"script": code, "name": self.script_name, "author": self.author, "for_new_ui": self.for_new_ui}
            else:
                raise Exception(
                    "Code for Browser Script, " + self.script_name + ", does not exist on disk at path: " + str(
                        code_file))
        except Exception as e:
            raise e


class MythicTask:
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
        for k,v in kwargs.items():
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
class PTTTaskOPSECPostTaskMessageResponse:
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
        for k,v in kwargs.items():
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
class PTTaskCreateTaskingMessageResponse:
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
        for k,v in kwargs.items():
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
class PTTaskMessageTaskData:
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
        for k,v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")
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
class PTTaskMessageCallbackData:
    def __init__(self,
                 id: int = 0,
                 agent_callback_id: str = "",
                 init_callback: str = "",
                 last_checkin: str = "",
                 user: str = "",
                 host: str = "",
                 pid: int = 0,
                 ip: str = "",
                 external_ip: str = "",
                 process_name: str = "",
                 description: str = "",
                 operator_id: int = 0,
                 active: bool = False,
                 registered_payload_id: int = 0,
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
                 **kwargs):
        self.ID = id
        self.AgentCallbackID = agent_callback_id
        self.InitCallback = init_callback
        self.LastCheckin = last_checkin
        self.User = user
        self.Host = host
        self.PID = pid
        self.Ip = ip
        self.ExternalIp = external_ip
        self.ProcessName = process_name
        self.Description = description
        self.OperatorID = operator_id
        self.Active = active
        self.RegisteredPayloadID = registered_payload_id
        self.IntegrityLevel = integrity_level
        self.Locked = locked
        self.OperationID = operation_id
        self.CryptoType = crypto_type
        self.DecKey = base64.b64decode(dec_key) if dec_key is not None else None
        self.EncKey = base64.b64decode(enc_key) if enc_key is not None else None
        self.Os = os
        self.Architecture = architecture
        self.Domain = domain
        self.ExtraInfo = extra_info
        self.SleepInfo = sleep_info
        for k,v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")
    def to_json(self):
        return {
            "id": self.ID,
        "agent_callback_id": self.AgentCallbackID,
        "init_callback": self.InitCallback,
        "last_checkin": self.LastCheckin,
        "user": self.User,
        "host": self.Host,
        "pid": self.PID,
        "ip": self.Ip,
        "external_ip": self.ExternalIp,
        "process_name": self.ProcessName,
        "description": self.Description,
        "operator_id": self.OperatorID,
        "active": self.Active,
        "registered_payload_id": self.RegisteredPayloadID,
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
class PTTaskMessagePayloadData:
    def __init__(self,
                 os: str = "",
                 uuid: str = "",
                 payload_type: str = "",
                 **kwargs):
        self.Os = os
        self.UuID = uuid
        self.PayloadType = payload_type
        for k,v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")
class PTTaskMessageAllData:
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
                             task_dictionary=task,)
        else:
            self.args = args
        for k,v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")

    def set_args(self, args: TaskArguments.__class__) -> None:
        self.args = args(command_line=self.Task.Params,
                         tasking_location=self.Task.TaskingLocation,
                         raw_command_line=self.Task.OriginalParams,)

class PTTaskCompletionFunctionMessage:
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
        for k,v in kwargs.items():
            logger.info(f"unknown kwarg {k} with value {v}")
class PTTaskCompletionFunctionMessageResponse:
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
        for k,v in kwargs.items():
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
class PTTaskProcessResponseMessageResponse:
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

class CommandBase(metaclass=ABCMeta):
    supported_ui_features: list[str] = []
    browser_script: BrowserScript = None
    script_only: bool = False
    attributes: CommandAttributes = None
    completion_functions: dict[str, Callable[[PTTaskCompletionFunctionMessage], Awaitable[PTTaskCompletionFunctionMessageResponse]]] = {}
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

commands: dict[str, list[CommandBase]] = {}
