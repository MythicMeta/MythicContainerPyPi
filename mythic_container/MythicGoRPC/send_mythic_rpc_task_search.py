import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_TASK_SEARCH = "mythic_rpc_task_search"


class MythicRPCTaskSearchMessage:
    def __init__(self,
                 TaskID: int,
                 SearchTaskID: int = None,
                 SearchTaskDisplayID: int = None,
                 SearchAgentTaskID: str = None,
                 SearchHost: str = None,
                 SearchCallbackID: int = None,
                 SearchCompleted: bool = None,
                 SearchCommandNames: list[str] = None,
                 SearchParams: str = None,
                 **kwargs):
        self.TaskID = TaskID
        self.SearchTaskID = SearchTaskID
        self.SearchTaskDisplayID = SearchTaskDisplayID
        self.SearchAgentTaskID = SearchAgentTaskID
        self.SearchHost = SearchHost
        self.SearchCallbackID = SearchCallbackID
        self.SearchCompleted = SearchCompleted
        self.SearchCommandNames = SearchCommandNames
        self.SearchParams = SearchParams
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")

    def to_json(self):
        return {
            "task_id": self.TaskID,
            "search_task_id": self.SearchTaskID,
            "search_task_display_id": self.SearchTaskDisplayID,
            "agent_task_id": self.SearchAgentTaskID,
            "host": self.SearchHost,
            "callback_id": self.SearchCallbackID,
            "completed": self.SearchCompleted,
            "command_names": self.SearchCommandNames,
            "params": self.SearchParams
        }


class MythicRPCTaskSearchData:
    def __init__(self,
                 id: int = None,
                 display_id: int = None,
                 agent_task_id: str = None,
                 command_name: str = None,
                 params: str = None,
                 timestamp: str = None,
                 callback_id: int = None,
                 status: str = None,
                 original_params: str = None,
                 display_params: str = None,
                 comment: str = None,
                 stdout: str = None,
                 stderr: str = None,
                 completed: bool = None,
                 operator_username: str = None,
                 opsec_pre_blocked: bool = None,
                 opsec_pre_message: str = None,
                 opsec_pre_bypassed: bool = None,
                 opsec_pre_bypass_role: str = None,
                 opsec_post_blocked: bool = None,
                 opsec_post_message: str = None,
                 opsec_post_bypassed: bool = None,
                 opsec_post_bypass_role: str = None,
                 parent_task_id: int = None,
                 subtask_callback_function: str = None,
                 subtask_callback_function_completed: bool = None,
                 group_callback_function: str = None,
                 group_callback_function_completed: bool = None,
                 completed_callback_function: str = None,
                 completed_callback_function_completed: bool = None,
                 subtask_group_name: str = None,
                 tasking_location: str = None,
                 parameter_group_name: str = None,
                 token_id: int = None,
                 **kwargs):
        self.TaskID = id
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
        self.OPSECPreBlocked = opsec_pre_blocked
        self.OPSECPREMessage = opsec_pre_message
        self.OPSECPREBypassed = opsec_pre_bypassed
        self.OPSECPREBypassRole = opsec_pre_bypass_role
        self.OPSECPOSTBlocked = opsec_post_blocked
        self.OPSECPOSTMessage = opsec_post_message
        self.OPSECPOSTBypassed = opsec_post_bypassed
        self.OPSECPOSTBypassRole = opsec_post_bypass_role
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
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")
    def to_json(self):
        return {
            "id": self.TaskID,
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
            "opsec_pre_blocked": self.OPSECPreBlocked,
            "opsec_pre_message": self.OPSECPREMessage,
            "opsec_pre_bypassed": self.OPSECPREBypassed,
            "opsec_pre_bypass_role": self.OPSECPREBypassRole,
            "opsec_post_blocked": self.OPSECPOSTBlocked,
            "opsec_post_message": self.OPSECPOSTMessage,
            "opsec_post_bypassed": self.OPSECPOSTBypassed,
            "opsec_post_bypass_role": self.OPSECPOSTBypassRole,
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
            "token_id": self.TokenID
        }

class MythicRPCTaskSearchMessageResponse:
    Tasks: list[MythicRPCTaskSearchData]

    def __init__(self,
                 success: bool = False,
                 error: str = "",
                 tasks: list[dict] = None,
                 **kwargs):
        self.Success = success
        self.Error = error
        self.Tasks = [MythicRPCTaskSearchData(**x) for x in tasks] if tasks is not None else []
        for k, v in kwargs.items():
            logger.info(f"Unknown kwarg {k} - {v}")


async def SendMythicRPCTaskSearch(
        msg: MythicRPCTaskSearchMessage) -> MythicRPCTaskSearchMessageResponse:
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=MYTHIC_RPC_TASK_SEARCH,
                                                                            body=msg.to_json())
    return MythicRPCTaskSearchMessageResponse(**response)
