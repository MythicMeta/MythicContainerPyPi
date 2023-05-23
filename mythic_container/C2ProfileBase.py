import pathlib
from enum import Enum
from abc import abstractmethod
import json
from collections.abc import Awaitable, Callable
from .logging import logger
import base64
import sys
from typing import List


class C2OPSECMessage:
    """Payload's C2 Profile configuration for OPSEC checking

    Attributes:
        Name (str): Name of the C2 Profile
        Parameters (dict): Dictionary of C2 Parameter name:value

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 parameters: dict,
                 **kwargs):
        self.Name = c2_profile_name
        self.Parameters = parameters
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self) -> dict:
        return {
            "c2_profile_name": self.Name,
            "parameters": self.Parameters
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2OPSECMessageResponse:
    """Status of running C2 Profile's opsec function

    Attributes:
        Success (bool): Did the OPSEC check succeed or fail
        Error (str): Error message if the OPSEC check failed
        Message (str): Informative message about the OPSEC check if there was no error

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2ConfigCheckMessage:
    """Payload's C2 Profile configuration for Configuration checking

    Attributes:
        Name (str): Name of the C2 Profile
        Parameters (dict): Dictionary of C2 Parameter name:value

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 parameters: dict,
                 **kwargs):
        self.Name = c2_profile_name
        self.Parameters = parameters
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "parameters": self.Parameters
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2ConfigCheckMessageResponse:
    """Status of running C2 Profile's config_check function

    Attributes:
        Success (bool): Did the config check succeed or fail
        Error (str): Error message if the config check failed
        Message (str): Informative message about the config check if there was no error

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2GetIOCMessage:
    """Payload's C2 Profile configuration for getting IOCs

    Attributes:
        Name (str): Name of the C2 Profile
        Parameters (dict): Dictionary of C2 Parameter name:value

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 parameters: dict,
                 **kwargs):
        self.Name = c2_profile_name
        self.Parameters = parameters
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "parameters": self.Parameters
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2GetIOCMessageResponseIOC:
    """An IOC to report back as part of a C2 Profile's get_ioc function

    Attributes:
        Type (str): The type of IOC (ex: Hash, URL)
        IOC (str): The actual IOC value
    """
    def __init__(self,
                 Type: str,
                 IOC: str):
        self.Type = Type
        self.IOC = IOC

    def to_json(self):
        return {
            "type": self.Type,
            "ioc": self.IOC
        }


class C2GetIOCMessageResponse:
    """Status of running C2 Profile's get_ioc function

    Attributes:
        Success (bool): Did the get ioc request succeed or fail
        Error (str): Error message if the get ioc request failed
        IOCs (List[C2GetIOCMessageResponseIOC]): List of the IOC values

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 IOCs: List[C2GetIOCMessageResponseIOC] = [],
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.IOCs = IOCs
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "iocs": self.IOCs
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2SampleMessageMessage:
    """Sample C2 message based on the Payload's configuration

    Attributes:
        Name (str): Name of the C2 Profile
        Parameters (dict): Dictionary of C2 Parameter name:value

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 parameters: dict,
                 **kwargs):
        self.Name = c2_profile_name
        self.Parameters = parameters
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "parameters": self.Parameters
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2SampleMessageMessageResponse:
    """Sample C2 Message based on the payload's configuration

    Attributes:
        Success (bool): Did the sample message generation succeed or fail
        Error (str): Error message if the sample message generation failed
        Message (str): Sample message to represent that C2 traffic would look like for this payload

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2GetDebugOutputMessage:
    """Try to get debug output from subprocess running internal server code

    Attributes:
        Name (str): Name of the C2 Profile

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 **kwargs):
        self.Name = c2_profile_name
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2GetDebugOutputMessageResponse:
    """Debug output from subprocesses running internal server

    Attributes:
        Success (bool): Were we able to get information from subprocess
        Error (str): Error message if the subprocess exited
        Message (str): Whatever output was generated from the subprocess
        InternalServerRunning (bool): Is the subprocess still running or not

    Functions:
        to_json(self): return dictionary form of class
    """

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
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message,
            "server_running": self.InternalServerRunning
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2GetFileMessage:
    """Fetch file from C2 Profile's server folder directory

    Attributes:
        Name (str): Name of the C2 Profile
        Filename (str): Name of the file to read

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 filename: str,
                 **kwargs):
        self.Name = c2_profile_name
        self.Filename = filename
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "filename": self.Filename
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2GetFileMessageResponse:
    """Contents or error from fetching a file

    Attributes:
        Success (bool): Did we successfully read the file or not
        Error (str): Error message if we failed to read the file
        Message (str): Contents of the file

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: bytes = b"",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": base64.b64encode(self.Message).decode(),
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2GetRedirectorRulesMessage:
    """Payload's C2 Profile configuration for generating Apache ModRewrite rules

    Attributes:
        Name (str): Name of the C2 Profile
        Parameters (dict): Dictionary of C2 Parameter name:value

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 parameters: dict,
                 **kwargs):
        self.Name = c2_profile_name
        self.Parameters = parameters
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "parameters": self.Parameters
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2GetRedirectorRulesMessageResponse:
    """Status of running C2 Profile's get redirector rules function

    Attributes:
        Success (bool): Did the redirector check succeed or fail
        Error (str): Error message if the redirector check failed
        Message (str): Apache ModRewrite rules

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2ListFileMessage:
    """List the contents of a C2 Profile's server folder directory

    Attributes:
        Name (str): Name of the C2 Profile

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 **kwargs):
        self.Name = c2_profile_name
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2ListFileMessageResponse:
    """List of filenames in the C2 Profile's server folder directory

    Attributes:
        Success (bool): Did the OPSEC check succeed or fail
        Error (str): Error message if the OPSEC check failed
        Files (list[str]): List of filenames

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Files: list[str] = [],
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Files = Files
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "files": self.Files,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2RemoveFileMessage:
    """Request to remove a file from a C2 Profile's server folder path

    Attributes:
        Name (str): Name of the C2 Profile
        Filename (str): Name of the file to remove

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 filename: str,
                 **kwargs):
        self.Name = c2_profile_name
        self.Filename = filename
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "filename": self.Filename
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2RemoveFileMessageResponse:
    """Status of removing the file

    Attributes:
        Success (bool): Did the file removal succeed or fail
        Error (str): Error message if the file removal failed

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2StartServerMessage:
    """Request to start a C2 Profile's internal server as a subprocess

    Attributes:
        Name (str): Name of the C2 Profile

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 **kwargs):
        self.Name = c2_profile_name
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2StartServerMessageResponse:
    """Status of running C2 Profile's internal server as a subprocess

    Attributes:
        Success (bool): Did the start subprocess succeed or fail
        Error (str): Error message if the subprocess failed to run for more than 3 seconds
        Message (str): Output from the first 3 seconds of the subprocess running
        InternalServerRunning (bool): Is the internal server subprocess still running or not

    Functions:
        to_json(self): return dictionary form of class
    """

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
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message,
            "server_running": self.InternalServerRunning
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2StopServerMessage:
    """Request to stop the C2 Profile's internal server subprocess

    Attributes:
        Name (str): Name of the C2 Profile

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 **kwargs):
        self.Name = c2_profile_name
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2StopServerMessageResponse:
    """Status of stopping the C2 Server's subprocess

    Attributes:
        Success (bool): Did the subprocesses successfully stop or not
        Error (str): Error message if the subprocess failed to stop
        Message (str): Any final output the subprocess was reporting
        InternalServerRunning (bool): Is the internal subprocess still running or not

    Functions:
        to_json(self): return dictionary form of class
    """

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
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message,
            "server_running": self.InternalServerRunning
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2WriteFileMessage:
    """Request to write a file to the C2 Profile's server folder directory

    Attributes:
        Name (str): Name of the C2 Profile
        Filename (str): Name of the file to create/overwrite
        Contents (bytes): Contents of the file to write

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 c2_profile_name: str,
                 filename: str,
                 contents: str,
                 **kwargs):
        self.Name = c2_profile_name
        self.Filename = filename
        self.Contents = base64.b64decode(contents)
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "c2_profile_name": self.Name,
            "filename": self.Filename,
            "contents": base64.b64encode(self.Contents)
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2WriteFileMessageResponse:
    """Status of writing the file to disk

    Attributes:
        Success (bool): Did the file get written or not
        Error (str): Error message if the file failed to write to disk
        Message (str): Informative message about the file getting written

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 Success: bool,
                 Error: str = "",
                 Message: bytes = b"",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Message = Message
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class C2OtherServiceRPCMessage:
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


class C2OtherServiceRPCMessageResponse:
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


class ParameterType(Enum):
    """Types of parameters available for C2 Profiles when building payloads

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
     """
    String = "String"
    ChooseOne = "ChooseOne"
    Array = "Array"
    Date = "Date"
    Dictionary = "Dictionary"
    Boolean = "Boolean"


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


class C2ProfileParameter:
    """C2Profile Parameter Definition for use when generating payloads

    Attributes:
        name (str): Name of the parameter for scripting and for when building payloads
        description (str): Informative description displayed when building a payload
        default_value (any): Default value to pre-populate
        randomize (bool): Should this value be randomized (requires format_string)
        format_string (str): A regex used for randomizing values if randomize is true
        parameter_type (ParameterType): The type of parameter this is
        required (bool): Is this parameter required to have a non-empty value or not
        verifier_regex (str): Regex used to verify that the user typed something appropriate
        choices (list[str]): Choices for ChooseOne parameter type
        dictionary_choices (list[DictionaryChoice]): Configuration options for the Dictionary parameter type
        crypto_type (bool): Indicate if this value should be used to generate a crypto key or not

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(
            self,
            name: str,
            description: str,
            default_value: any = None,
            randomize: bool = False,
            format_string: str = "",
            parameter_type: ParameterType = ParameterType.String,
            required: bool = True,
            verifier_regex: str = "",
            choices: list[str] = None,
            dictionary_choices: list[DictionaryChoice] = None,
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
        self.dictionary_choices = dictionary_choices

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


class C2Profile:
    """C2 Profile to import and sync with Mythic

    Attributes:
        name (str): Name of the profile
        description (str): Description of the profile
        author (str): Author of the profile
        is_p2p (bool): Is the profile defining P2P communications or egress communications
        parameters (list[C2ProfileParameter]): Definition of the parameters for the profile used when building a payload
        server_folder_path (pathlib.Path): Path to the folder that contains `config.json`
        server_binary_path (pathlib.Path): Path to the binary that gets executed when "Start" is clicked in the UI
        custom_rpc_functions: Dictionary of RPC name to awaitable RPC function that other services can call

    Functions:
        opsec

        config_check

        redirect_rules

        get_ioc

        sample_message

    """

    async def opsec(self, inputMsg: C2OPSECMessage) -> C2OPSECMessageResponse:
        """Check payload's C2 configuration for OPSEC issues

        :param inputMsg: Payload's C2 Profile configuration
        :return: C2OPSECMessageResponse detailing the results of the OPSEC check
        """
        response = C2OPSECMessageResponse(Success=True)
        response.Message = "Not Implemented, passing by default"
        response.Message += f"\nInput: {json.dumps(inputMsg.to_json(), indent=4)}"
        return response

    async def config_check(self, inputMsg: C2ConfigCheckMessage) -> C2ConfigCheckMessageResponse:
        """Check a payload's C2 configuration to see if it matches the local configuration

        :param inputMsg: Payload's C2 Profile configuration
        :return: C2ConfigCheckMessageResponse detailing the results of the configuration check
        """
        response = C2ConfigCheckMessageResponse(Success=True)
        response.Message = "Not Implemented"
        response.Message += f"\nInput: {json.dumps(inputMsg.to_json(), indent=4)}"
        return response

    async def redirect_rules(self, inputMsg: C2GetRedirectorRulesMessage) -> C2GetRedirectorRulesMessageResponse:
        """Generate Apache ModRewrite rules given the Payload's C2 configuration

        :param inputMsg: Payload's C2 Profile configuration
        :return: C2GetRedirectorRulesMessageResponse detailing some Apache ModRewrite rules for the payload
        """
        response = C2GetRedirectorRulesMessageResponse(Success=True)
        response.Message = "Not Implemented"
        response.Message += f"\nInput: {json.dumps(inputMsg.to_json(), indent=4)}"
        return response

    async def get_ioc(self, inputMsg: C2GetIOCMessage) -> C2GetIOCMessageResponse:
        """Generate IOCs for the network traffic associated with the specified c2 configuration

        :param inputMsg: Payload's C2 Profile configuration
        :return: C2GetIOCMessageResponse detailing some IOCs
        """
        response = C2GetIOCMessageResponse(Success=True)
        response.IOCs = []
        return response

    async def sample_message(self, inputMsg: C2SampleMessageMessage) -> C2SampleMessageMessageResponse:
        """Generate a sample message for this c2 profile based on the configuration specified

        :param inputMsg: Payload's C2 Profile configuration
        :return: C2SampleMessageMessageResponse detailing a sample message
        """
        response = C2SampleMessageMessageResponse(Success=True)
        response.Message = "Not Implemented"
        response.Message += f"\nInput: {json.dumps(inputMsg.to_json(), indent=4)}"
        return response

    custom_rpc_functions: dict[
        str, Callable[[C2OtherServiceRPCMessage], Awaitable[C2OtherServiceRPCMessageResponse]]] = {}
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
            logger.exception(
                "Must supply server_binary_path as pathlib.Path pointing to the binary to run when the server starts")
            sys.exit(1)
        elif not isinstance(self.server_binary_path, pathlib.Path):
            logger.exception("Wrong type for server_binary_path - should be pathlib.Path")
            sys.exit(1)
        elif self.server_folder_path is None:
            logger.exception(
                "Must supply server_folder_path as pathlib.Path pointing to folder where your c2 files exist")
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

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


c2Profiles: dict[str, C2Profile] = {}
runningServers: dict[str, dict] = {}
