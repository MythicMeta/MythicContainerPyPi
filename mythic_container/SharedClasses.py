import json
import base64


class ContainerOnStartMessage:
    def __init__(self,
                 container_name: str = "",
                 operation_id: int = 0,
                 server_name: str = "",
                 apitoken: str = "",
                 **kwargs):
        self.ContainerName = container_name
        self.OperationID = operation_id
        self.ServerName = server_name
        self.APIToken = apitoken

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "operation_id": self.OperationID,
            "server_name": self.ServerName,
            "apitoken": self.APIToken
        }


class ContainerOnStartMessageResponse:
    def __init__(self,
                 ContainerName: str = "",
                 EventLogInfoMessage: str = "",
                 EventLogErrorMessage: str = "",
                 RestartInternalServer: bool = False
                 ):
        self.ContainerName = ContainerName
        self.EventLogInfoMessage = EventLogInfoMessage
        self.EventLogErrorMessage = EventLogErrorMessage
        self.RestartInternalServer = RestartInternalServer

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "stdout": self.EventLogInfoMessage,
            "stderr": self.EventLogErrorMessage
        }


class GetFileMessage:
    """Fetch file from C2 Profile's server folder directory

    Attributes:
        Name (str): Name of the C2 Profile
        Filename (str): Name of the file to read

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 container_name: str,
                 filename: str,
                 **kwargs):
        self.Name = container_name
        self.Filename = filename

    def to_json(self):
        return {
            "container_name": self.Name,
            "filename": self.Filename
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class GetFileMessageResponse:
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

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": base64.b64encode(self.Message).decode(),
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ListFileMessage:
    """List the contents of a C2 Profile's server folder directory

    Attributes:
        Name (str): Name of the C2 Profile

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 container_name: str,
                 **kwargs):
        self.Name = container_name

    def to_json(self):
        return {
            "container_name": self.Name,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class ListFileMessageResponse:
    """List of filenames in the C2 Profile's server folder directory

    Attributes:
        Success (bool): Did the list check succeed or fail
        Error (str): Error message if the list check failed
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

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "files": self.Files,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class RemoveFileMessage:
    """Request to remove a file from a C2 Profile's server folder path

    Attributes:
        Name (str): Name of the C2 Profile
        Filename (str): Name of the file to remove

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 container_name: str,
                 filename: str,
                 **kwargs):
        self.Name = container_name
        self.Filename = filename

    def to_json(self):
        return {
            "container_name": self.Name,
            "filename": self.Filename
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class RemoveFileMessageResponse:
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

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class WriteFileMessage:
    """Request to write a file to the C2 Profile's server folder directory

    Attributes:
        Name (str): Name of the C2 Profile
        Filename (str): Name of the file to create/overwrite
        Contents (bytes): Contents of the file to write

    Functions:
        to_json(self): return dictionary form of class
    """

    def __init__(self,
                 container_name: str,
                 filename: str,
                 contents: str,
                 **kwargs):
        self.Name = container_name
        self.Filename = filename
        self.Contents = base64.b64decode(contents)

    def to_json(self):
        return {
            "container_name": self.Name,
            "filename": self.Filename,
            "contents": base64.b64encode(self.Contents)
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


class WriteFileMessageResponse:
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

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)
