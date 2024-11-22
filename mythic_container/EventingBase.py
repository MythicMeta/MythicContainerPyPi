from collections.abc import Callable, Awaitable
from typing import Union

import mythic_container
from .logging import logger
import base64
import json
from .MythicCommandBase import PTTaskMessageTaskData
from .SharedClasses import ContainerOnStartMessage, ContainerOnStartMessageResponse


class ConditionalCheckEventingMessage:
    def __init__(self,
                 eventstepinstance_id: int = 0,
                 function_name: str = "",
                 container_name: str = "",
                 environment: dict = {},
                 inputs: dict = {},
                 action_data: dict = {},
                 **kwargs):
        self.EventStepInstanceID = eventstepinstance_id
        self.FunctionName = function_name
        self.ContainerName = container_name
        self.Environment = environment
        self.Inputs = inputs
        self.ActionData = action_data

    def to_json(self):
        return {
            "eventstepinstance_id": self.EventStepInstanceID,
            "function_name": self.FunctionName,
            "container_name": self.ContainerName,
            "environment": self.Environment,
            "inputs": self.Inputs,
            "action_data": self.ActionData
        }


class ConditionalCheckEventingMessageResponse:
    def __init__(self,
                 EventStepInstanceID: int = 0,
                 Success: bool = True,
                 StdErr: str = "",
                 StdOut: str = "",
                 Outputs: dict = {},
                 SkipStep: bool = False,
                 **kwargs):
        self.EventStepInstanceID = EventStepInstanceID
        self.Success = Success
        self.StdErr = StdErr
        self.StdOut = StdOut
        self.Outputs = Outputs
        self.SkipStep = SkipStep

    def to_json(self):
        return {
            "eventstepinstance_id": self.EventStepInstanceID,
            "success": self.Success,
            "stderr": self.StdErr,
            "stdout": self.StdOut,
            "outputs": self.Outputs,
            "skip_step": self.SkipStep,
        }


class NewCustomEventingMessage:
    def __init__(self,
                 container_name: str = "",
                 eventstepinstance_id: int = 0,
                 function_name: str = "",
                 environment: dict = {},
                 inputs: dict = {},
                 action_data: dict = {}):
        self.ContainerName = container_name
        self.EventStepInstanceID = eventstepinstance_id
        self.FunctionName = function_name
        self.Environment = environment
        self.Inputs = inputs
        self.ActionData = action_data

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "eventstepinstance_id": self.EventStepInstanceID,
            "function_name": self.FunctionName,
            "environment": self.Environment,
            "inputs": self.Inputs,
            "action_data": self.ActionData
        }


class NewCustomEventingMessageResponse:
    def __init__(self,
                 EventStepInstanceID: int = 0,
                 Success: bool = True,
                 StdErr: str = "",
                 StdOut: str = "",
                 Outputs: dict = {},
                 **kwargs):
        self.EventStepInstanceID = EventStepInstanceID
        self.Success = Success
        self.StdErr = StdErr
        self.StdOut = StdOut
        self.Outputs = Outputs

    def to_json(self):
        return {
            "eventstepinstance_id": self.EventStepInstanceID,
            "success": self.Success,
            "stderr": self.StdErr,
            "stdout": self.StdOut,
            "outputs": self.Outputs,
        }


class ResponseInterceptMessage:
    def __init__(self,
                 eventstepinstance_id: int = 0,
                 response_id: int = 0,
                 callback_id: int = 0,
                 callback_display_id: int = 0,
                 agent_callback_id: str = "",
                 container_name: str = "",
                 environment: dict = {},
                 inputs: dict = {},
                 action_data: dict = {},
                 **kwargs):
        self.ContainerName = container_name
        self.EventStepInstanceID = eventstepinstance_id
        self.ResponseID = response_id
        self.CallbackID = callback_id
        self.CallbackDisplayID = callback_display_id
        self.AgentCallbackID = agent_callback_id
        self.Environment = environment
        self.Inputs = inputs
        self.ActionData = action_data

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "eventstepinstance_id": self.EventStepInstanceID,
            "response_id": self.ResponseID,
            "callback_id": self.CallbackID,
            "callback_display_id": self.CallbackDisplayID,
            "agent_callback_id": self.AgentCallbackID,
            "environment": self.Environment,
            "inputs": self.Inputs,
            "action_data": self.ActionData,
        }


class ResponseInterceptMessageResponse:
    def __init__(self,
                 EventStepInstanceID: int = 0,
                 ResponseID: int = 0,
                 Success: bool = True,
                 StdErr: str = "",
                 StdOut: str = "",
                 Outputs: dict = {},
                 Response: str = "",
                 **kwargs):
        self.EventStepInstanceID = EventStepInstanceID
        self.Success = Success
        self.StdErr = StdErr
        self.StdOut = StdOut
        self.Outputs = Outputs
        self.ResponseID = ResponseID
        self.Response = Response

    def to_json(self):
        return {
            "eventstepinstance_id": self.EventStepInstanceID,
            "success": self.Success,
            "stderr": self.StdErr,
            "stdout": self.StdOut,
            "outputs": self.Outputs,
            "response_id": self.ResponseID,
            "response": self.Response,
        }


class TaskInterceptMessage:
    def __init__(self,
                 eventstepinstance_id: int = 0,
                 task_id: int = 0,
                 callback_id: int = 0,
                 container_name: str = "",
                 environment: dict = {},
                 inputs: dict = {},
                 action_data: dict = {},
                 **kwargs):
        self.ContainerName = container_name
        self.TaskID = task_id
        self.EventStepInstanceID = eventstepinstance_id
        self.CallbackID = callback_id
        self.Environment = environment
        self.Inputs = inputs
        self.ActionData = action_data

    def to_json(self):
        return {
            "container_name": self.ContainerName,
            "eventstepinstance_id": self.EventStepInstanceID,
            "task_id": self.TaskID,
            "callback_id": self.CallbackID,
            "environment": self.Environment,
            "inputs": self.Inputs,
            "action_data": self.ActionData,
        }


class TaskInterceptMessageResponse:
    def __init__(self,
                 EventStepInstanceID: int = 0,
                 TaskID: int = 0,
                 Success: bool = True,
                 StdErr: str = "",
                 StdOut: str = "",
                 Outputs: dict = {},
                 BlockTask: bool = False,
                 BypassRole: str = "",
                 BypassMessage: str = "",
                 **kwargs):
        self.EventStepInstanceID = EventStepInstanceID
        self.Success = Success
        self.StdErr = StdErr
        self.StdOut = StdOut
        self.Outputs = Outputs
        self.TaskID = TaskID
        self.BlockTask = BlockTask
        self.BypassRole = BypassRole
        self.BypassMessage = BypassMessage

    def to_json(self):
        return {
            "eventstepinstance_id": self.EventStepInstanceID,
            "success": self.Success,
            "stderr": self.StdErr,
            "stdout": self.StdOut,
            "outputs": self.Outputs,
            "task_id": self.TaskID,
            "block_task": self.BlockTask,
            "bypass_role": self.BypassRole,
            "bypass_message": self.BypassMessage,
        }


class CustomFunctionDefinition:
    def __init__(self,
                 Name: str = "",
                 Description: str = "",
                 Function: Callable[[NewCustomEventingMessage], Awaitable[NewCustomEventingMessageResponse]] = None):
        self.Name = Name
        self.Description = Description
        self.Function = Function

    def to_json(self):
        return {
            "name": self.Name,
            "description": self.Description,
        }


class ConditionalCheckDefinition:
    def __init__(self,
                 Name: str = "",
                 Description: str = "",
                 Function: Callable[[ConditionalCheckEventingMessage], Awaitable[ConditionalCheckEventingMessageResponse]] = None):
        self.Name = Name
        self.Description = Description
        self.Function = Function

    def to_json(self):
        return {
            "name": self.Name,
            "description": self.Description,
        }


class Eventing:
    """Eventing definition class for performing custom eventing actions within Mythic


    Attributes:
        name:
            name for this auth service that appears in the Mythic UI
        description:
            description about what this auth service provides that appears in the Mythic UI
        custom_functions:
            an array of CustomFunctionDefinition entries that provide name, description, and function implementations
        conditional_checks:
            an array of ConditionalCheckDefinition entries that provide name, description, and function implementations
    Functions:
        task_intercept_function:
        response_intercept_function:
    """
    name: str = ""
    description: str = ""

    task_intercept_function: Callable[[TaskInterceptMessage], Awaitable[TaskInterceptMessageResponse]] = None
    response_intercept_function: Callable[
        [ResponseInterceptMessage], Awaitable[ResponseInterceptMessageResponse]] = None
    custom_functions: [CustomFunctionDefinition] = []
    conditional_checks: [ConditionalCheckDefinition] = []

    async def on_container_start(self, message: ContainerOnStartMessage) -> ContainerOnStartMessageResponse:
        return ContainerOnStartMessageResponse(ContainerName=self.name)

    def get_sync_message(self):
        custom = [x.to_json() for x in self.custom_functions]
        conditional = [x.to_json() for x in self.conditional_checks]
        subscriptions = custom + conditional
        if self.task_intercept_function is not None:
            subscriptions.append({
                "name":        "task_intercept",
                "description": "Intercept Task execution before it gets to an agent and potentially block it",
            })
        if self.response_intercept_function is not None:
            subscriptions.append({
                "name":        "response_intercept",
                "description": "Intercept User Output Responses they get sent to the user",
            })
        subscriptions = [json.dumps(x) for x in subscriptions]
        return {
            "name": self.name,
            "type": "eventing",
            "description": self.description,
            "subscriptions": subscriptions
        }


eventingServices: dict[str, Eventing] = {}


async def SendMythicRPCSyncEventing(eventing_name: str) -> bool:
    try:
        eventing_services = Eventing.__subclasses__()
        for cls in eventing_services:
            event = cls()
            if event.name == "":
                continue
            if event.name == eventing_name:
                eventingServices.pop(eventing_name, None)
                eventingServices[event.name] = event
                await mythic_container.mythic_service.syncEventingData(event)
                return True
        return False
    except Exception as e:
        return False