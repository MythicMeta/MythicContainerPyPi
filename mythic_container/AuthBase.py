from collections.abc import Callable, Awaitable
from typing import Union

import mythic_container
from .logging import logger
import base64
import json
from .MythicCommandBase import PTTaskMessageTaskData
from .SharedClasses import ContainerOnStartMessage, ContainerOnStartMessageResponse


class GetIDPMetadataMessage:
    def __init__(self,
                 container_name: str = "",
                 server_name: str = "",
                 idp_name: str = "",
                 **kwargs):
        self.ContainerName = container_name
        self.ServerName = server_name
        self.IDPName = idp_name

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "server_name": self.ServerName,
            "idp_name": self.IDPName
        }


class GetIDPMetadataMessageResponse:
    def __init__(self,
                 Success: bool = True,
                 Error: str = "",
                 Metadata: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Metadata = Metadata

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "metadata": self.Metadata
        }


class GetIDPRedirectMessage:
    def __init__(self,
                 container_name: str = "",
                 server_name: str = "",
                 idp_name: str = "",
                 request_url: str = "",
                 request_headers: dict = {},
                 request_cookies: dict = {},
                 request_query: dict = {}):
        self.ContainerName = container_name
        self.ServerName = server_name
        self.IDPName = idp_name
        self.RequestURL = request_url
        self.RequestHeaders = request_headers
        self.RequestCookies = request_cookies
        self.RequestQuery = request_query

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "server_name": self.ServerName,
            "idp_name": self.IDPName,
            "request_url": self.RequestURL,
            "request_headers": self.RequestHeaders,
            "request_cookies": self.RequestCookies,
            "request_query": self.RequestQuery
        }


class GetIDPRedirectMessageResponse:
    def __init__(self,
                 Success: bool = True,
                 Error: str = "",
                 RedirectURL: str = "",
                 RedirectHeaders: dict = {},
                 RedirectCookies: dict = {}):
        self.Success = Success
        self.Error = Error
        self.RedirectURL = RedirectURL
        self.RedirectHeaders = RedirectHeaders
        self.RedirectCookies = RedirectCookies

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "redirect_url": self.RedirectURL,
            "redirect_headers": self.RedirectHeaders,
            "redirect_cookies": self.RedirectCookies
        }


class GetNonIDPMetadataMessage:
    def __init__(self,
                 container_name: str = "",
                 server_name: str = "",
                 nonidp_name: str = "",
                 **kwargs):
        self.ContainerName = container_name
        self.ServerName = server_name
        self.NonIDPName = nonidp_name

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "server_name": self.ServerName,
            "nonidp_name": self.NonIDPName
        }


class GetNonIDPMetadataMessageResponse:
    def __init__(self,
                 Success: bool = True,
                 Error: str = "",
                 Metadata: str = "",
                 **kwargs):
        self.Success = Success
        self.Error = Error
        self.Metadata = Metadata

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "metadata": self.Metadata
        }


class GetNonIDPRedirectMessage:
    def __init__(self,
                 container_name: str = "",
                 server_name: str = "",
                 nonidp_name: str = ""):
        self.ContainerName = container_name
        self.ServerName = server_name
        self.NonIDPName = nonidp_name

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "server_name": self.ServerName,
            "nonidp_name": self.NonIDPName,
        }


class GetNonIDPRedirectMessageResponse:
    def __init__(self,
                 Success: bool = True,
                 Error: str = "",
                 RequestFields: [str] = []):
        self.Success = Success
        self.Error = Error
        self.RequestFields = RequestFields

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "request_fields": self.RequestFields,
        }


class ProcessIDPResponseMessage:
    def __init__(self,
                 container_name: str = "",
                 server_name: str = "",
                 idp_name: str = "",
                 request_url: str = "",
                 request_headers: dict = {},
                 request_cookies: dict = {},
                 request_query: dict = {},
                 request_body: str = ""):
        self.ContainerName = container_name
        self.ServerName = server_name
        self.IDPName = idp_name
        self.RequestURL = request_url
        self.RequestHeaders = request_headers
        self.RequestCookies = request_cookies
        self.RequestQuery = request_query
        self.RequestBody = request_body

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "server_name": self.ServerName,
            "idp_name": self.IDPName,
            "request_url": self.RequestURL,
            "request_headers": self.RequestHeaders,
            "request_cookies": self.RequestCookies,
            "request_query": self.RequestQuery,
            "request_body": self.RequestBody
        }


class ProcessIDPResponseMessageResponse:
    def __init__(self,
                 SuccessfulAuthentication: bool = False,
                 Error: str = "",
                 Email: str = "", ):
        self.SuccessfulAuthentication = SuccessfulAuthentication
        self.Error = Error
        self.Email = Email

    def to_json(self):
        return {
            "successful_authentication": self.SuccessfulAuthentication,
            "error": self.Error,
            "email": self.Email,
        }


class ProcessNonIDPResponseMessage:
    def __init__(self,
                 container_name: str = "",
                 server_name: str = "",
                 idp_name: str = "",
                 request_values: dict = {}):
        self.ContainerName = container_name
        self.ServerName = server_name
        self.IDPName = idp_name
        self.RequestValues = request_values

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "server_name": self.ServerName,
            "idp_name": self.IDPName,
            "request_values": self.RequestValues
        }


class ProcessNonIDPResponseMessageResponse:
    def __init__(self,
                 SuccessfulAuthentication: bool = False,
                 Error: str = "",
                 Email: str = "", ):
        self.SuccessfulAuthentication = SuccessfulAuthentication
        self.Error = Error
        self.Email = Email

    def to_json(self):
        return {
            "successful_authentication": self.SuccessfulAuthentication,
            "error": self.Error,
            "email": self.Email,
        }


class Auth:
    """Auth definition class for performing custom auth within Mythic


    Attributes:
        name:
            name for this auth service that appears in the Mythic UI
        description:
            description about what this auth service provides that appears in the Mythic UI
        idp_services:
            list of names of IDP services you want to expose into the Mythic UI for users to select
        non_idp_services:
            list of names of Non-IDP auth options you want to expose into the Mythic UI for users to select

    Functions:

    """
    name: str = ""
    description: str = ""
    idp_services: [str] = []
    non_idp_services: [str] = []

    get_idp_metadata: Callable[[GetIDPMetadataMessage], Awaitable[GetIDPMetadataMessageResponse]] = None
    get_idp_redirect: Callable[[GetIDPRedirectMessage], Awaitable[GetIDPRedirectMessageResponse]] = None
    process_idp_response: Callable[[ProcessIDPResponseMessage], Awaitable[ProcessIDPResponseMessageResponse]] = None
    get_non_idp_metadata: Callable[[GetNonIDPMetadataMessage], Awaitable[GetNonIDPMetadataMessageResponse]] = None
    get_non_idp_redirect: Callable[[GetNonIDPRedirectMessage], Awaitable[GetNonIDPRedirectMessageResponse]] = None
    process_non_idp_response: Callable[[ProcessNonIDPResponseMessage], Awaitable[ProcessNonIDPResponseMessageResponse]] = None

    async def on_container_start(self, message: ContainerOnStartMessage) -> ContainerOnStartMessageResponse:
        return ContainerOnStartMessageResponse(ContainerName=self.name)

    def get_sync_message(self):
        idp_subs = [json.dumps({"name": x, "type": "idp"}) for x in self.idp_services]
        non_idp_subs = [json.dumps({"name": x, "type": "nonidp"}) for x in self.non_idp_services]
        return {
            "name": self.name,
            "type": "auth",
            "description": self.description,
            "subscriptions": idp_subs + non_idp_subs
        }


authServices: dict[str, Auth] = {}


async def SendMythicRPCSyncAuth(auth_name: str) -> bool:
    try:
        auth_services = Auth.__subclasses__()
        for cls in auth_services:
            auth = cls()
            if auth.name == "":
                continue
            if auth.name == auth_name:
                authServices.pop(auth_name, None)
                authServices[auth.name] = auth
                await mythic_container.mythic_service.syncAuthData(auth)
                return True
        return False
    except Exception as e:
        return False