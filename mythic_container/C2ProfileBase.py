import pathlib
from enum import Enum
from abc import abstractmethod
import json
from collections.abc import Awaitable, Callable
from .logging import logger
import base64
import sys


class C2OPSECMessage:
    def __init__(self,
                 c2_profile_name: str,
                 parameters: dict,
                 **kwargs):
        self.Name = c2_profile_name
        self.Parameters = parameters
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "parameters": self.Parameters
        }
class C2OPSECMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message
        }
class C2ConfigCheckMessage:
    def __init__(self,
                 c2_profile_name: str,
                 parameters: dict,
                 **kwargs):
        self.Name = c2_profile_name
        self.Parameters = parameters
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "parameters": self.Parameters
        }
class C2ConfigCheckMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message
        }
class C2GetDebugOutputMessage:
    def __init__(self,
                 c2_profile_name: str,
                 **kwargs):
        self.Name = c2_profile_name
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
        }
class C2GetDebugOutputMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 InternalServerRunning: bool = False,
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        self.InternalServerRunning = InternalServerRunning
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message,
            "server_running": self.InternalServerRunning
        }
class C2GetFileMessage:
    def __init__(self,
                 c2_profile_name: str,
                 filename: str,
                 **kwargs):
        self.Name = c2_profile_name
        self.Filename = filename
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "filename": self.Filename
        }
class C2GetFileMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: bytes = b"",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": base64.b64encode(self.Message).decode(),
        }
class C2GetRedirectorRulesMessage:
    def __init__(self,
                 c2_profile_name: str,
                 parameters: dict,
                 **kwargs):
        self.Name = c2_profile_name
        self.Parameters = parameters
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "parameters": self.Parameters
        }
class C2GetRedirectorRulesMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message
        }
class C2ListFileMessage:
    def __init__(self,
                 c2_profile_name: str,
                 **kwargs):
        self.Name = c2_profile_name
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
        }
class C2ListFileMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Files: list[str] = [],
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Files = Files
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "files": self.Files,
        }
class C2RemoveFileMessage:
    def __init__(self,
                 c2_profile_name: str,
                 filename: str,
                 **kwargs):
        self.Name = c2_profile_name
        self.Filename = filename
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "filename": self.Filename
        }
class C2RemoveFileMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
        }
class C2StartServerMessage:
    def __init__(self,
                 c2_profile_name: str,
                 **kwargs):
        self.Name = c2_profile_name
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
        }
class C2StartServerMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 InternalServerRunning: bool = False,
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        self.InternalServerRunning = InternalServerRunning
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message,
            "server_running": self.InternalServerRunning
        }
class C2StopServerMessage:
    def __init__(self,
                 c2_profile_name: str,
                 **kwargs):
        self.Name = c2_profile_name
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
        }
class C2StopServerMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 InternalServerRunning: bool = False,
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        self.InternalServerRunning = InternalServerRunning
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message,
            "server_running": self.InternalServerRunning
        }
class C2WriteFileMessage:
    def __init__(self,
                 c2_profile_name: str,
                 filename: str,
                 contents: str,
                 **kwargs):
        self.Name = c2_profile_name
        self.Filename = filename
        self.Contents = base64.b64decode(contents)
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "filename": self.Filename,
            "contents": base64.b64encode(self.Contents)
        }
class C2WriteFileMessageResponse:
    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: bytes = b"",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k,v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message,
        }
class C2OtherServiceRPCMessage:
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
class C2OtherServiceRPCMessageResponse:
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


class ParameterType(Enum):
    String = "String"
    ChooseOne = "ChooseOne"
    Array = "Array"
    Date = "Date"
    Dictionary = "Dictionary"
    Boolean = "Boolean"


class C2ProfileParameter:
    def __init__(
        self,
        name: str,
        description: str,
        default_value: str = None,
        randomize: bool = False,
        format_string: str = "",
        parameter_type: ParameterType = ParameterType.String,
        required: bool = True,
        verifier_regex: str = "",
        choices: [str] = None,
        crypto_type: bool = False,
    ):
        self.name = name
        self.description = description
        self.randomize = randomize
        self.format_string = format_string
        self.parameter_type = parameter_type
        self.required = required
        self.verifier_regex = verifier_regex
        self.choices = choices
        self.default_value = default_value
        self.crypto_type = crypto_type


    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "default_value": self.default_value if self.parameter_type not in [ParameterType.Array, ParameterType.Dictionary] else json.dumps(self.default_value),
            "randomize": self.randomize,
            "format_string": self.format_string,
            "required": self.required,
            "parameter_type": self.parameter_type.value,
            "verifier_regex": self.verifier_regex,
            "crypto_type": self.crypto_type,
            "choices": self.choices,
        }


class C2Profile:

    async def opsec(self, inputMsg: C2OPSECMessage) -> C2OPSECMessageResponse:
        response = C2OPSECMessageResponse(Success=True)
        response.Message = "Not Implemented, passing by default"
        response.Message += f"\nInput: {json.dumps(inputMsg.to_json(), indent=4)}"
        return response

    async def config_check(self, inputMsg: C2ConfigCheckMessage) -> C2ConfigCheckMessageResponse:
        response = C2ConfigCheckMessageResponse(Success=True)
        response.Message = "Not Implemented"
        response.Message += f"\nInput: {json.dumps(inputMsg.to_json(), indent=4)}"
        return response

    async def redirect_rules(self, inputMsg: C2GetRedirectorRulesMessage) -> C2GetRedirectorRulesMessageResponse:
        response = C2GetRedirectorRulesMessageResponse(Success=True)
        response.Message = "Not Implemented"
        response.Message += f"\nInput: {json.dumps(inputMsg.to_json(), indent=4)}"
        return response

    custom_rpc_functions: dict[str, Callable[[C2OtherServiceRPCMessage], Awaitable[C2OtherServiceRPCMessageResponse]]] = {}
    server_folder_path: pathlib.Path
    server_binary_path: pathlib.Path

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def author(self):
        pass

    @property
    @abstractmethod
    def is_p2p(self):
        pass

    @property
    @abstractmethod
    def is_server_routed(self):
        pass

    @property
    @abstractmethod
    def parameters(self):
        pass

    def to_json(self):
        if self.server_binary_path is None:
            logger.exception("Must supply server_binary_path as pathlib.Path pointing to the binary to run when the server starts")
            sys.exit(1)
        elif not isinstance(self.server_binary_path, pathlib.Path):
            logger.exception("Wrong type for server_binary_path - should be pathlib.Path")
            sys.exit(1)
        elif self.server_folder_path is None:
            logger.exception("Must supply server_folder_path as pathlib.Path pointing to folder where your c2 files exist")
            sys.exit(1)
        elif not isinstance(self.server_folder_path, pathlib.Path):
            logger.exception("Wrong type for server_folder_path - should be pathlib.Path")
            sys.exit(1)
        return {
            "c2_profile": {
                "name": self.name,
                "description": self.description,
                "author": self.author,
                "is_p2p": self.is_p2p,
                "is_server_routed": self.is_server_routed,
            },
            "parameters": [x.to_json() for x in self.parameters]
        }

c2Profiles: dict[str, C2Profile] = {}
runningServers: dict[str, dict] = {}