from .logging import logger
import ujson
from . import PayloadBuilder
from . import MythicCommandBase
import traceback
import mythic_container
from .utils_mythic_file_transfer import sendFileToMythic
import asyncio
from mythic_container.MythicRPC import *

OPSEC_ROLE_LEAD = "lead"
OPSEC_ROLE_OPERATOR = "operator"
OPSEC_ROLE_OTHER_OPERATOR = "other_operator"


async def makePayloadBuildResponse(buildMessage: dict, buildResponse: PayloadBuilder.BuildResponse) -> dict:
    try:
        response = {
            "uuid": str(buildMessage["uuid"]),
            "agent_file_id": str(buildMessage["payload_file_uuid"]),
            "success": True if str(buildResponse.get_status()) == "success" else False,
            "build_stderr": str(buildResponse.get_build_stderr()),
            "build_stdout": str(buildResponse.get_build_stdout()),
            "build_message": str(buildResponse.get_build_message()),
            "updated_command_list": buildResponse.get_updated_command_list(),
            "updated_filename": buildResponse.get_updated_filename()
        }
        if not response["success"]:
            if response["build_stderr"] == "":
                response["build_stderr"] = response["build_message"]
        await uploadPayloadBuildResponse(buildMessage, buildResponse)
        return response
    except Exception as e:
        logger.exception(f"Failed to generate payload build response: {e}")
        return {}


async def uploadPayloadBuildResponse(buildMessage: dict, buildResponse: PayloadBuilder.BuildResponse) -> None:
    await sendFileToMythic(buildResponse.get_payload(), buildMessage["payload_file_uuid"])


async def buildWrapper(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["payload_type"]:
                # go through all the data from rabbitmq to make the proper classes
                commands = PayloadBuilder.CommandList(msgDict["commands"])
                # go through all the data from rabbitmq to make the proper classes
                c2info_list = []
                if msgDict["c2profiles"] is not None:
                    for c2 in msgDict["c2profiles"]:
                        params = c2.pop("parameters", None)
                        c2info_list.append(
                            PayloadBuilder.C2ProfileParameters(
                                parameters=params, c2profile=c2
                            )
                        )
                wrapper_bytes = None
                if "wrapped_payload_uuid" in msgDict and msgDict["wrapped_payload_uuid"] is not None:
                    wrapper_bytes = await getFileFromMythic(msgDict["wrapped_payload_uuid"])
                agent_builder = pt.__class__(
                    uuid=msgDict["uuid"],
                    c2info=c2info_list,
                    filename=msgDict["filename"],
                    selected_os=msgDict["selected_os"],
                    commands=commands,
                    wrapped_payload=wrapper_bytes,
                    wrapped_payload_uuid=msgDict["wrapped_payload_uuid"] if "wrapped_payload_uuid" in msgDict else None
                )
                try:
                    await agent_builder.set_and_validate_build_parameters(msgDict["build_parameters"])
                    build_resp = await agent_builder.build()
                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                        queue=mythic_container.PT_BUILD_RESPONSE_ROUTING_KEY,
                        body=await makePayloadBuildResponse(msgDict, build_resp)
                    )

                except Exception as b:
                    logger.exception(f"[-] Failed to process build function for agent {pt.name}")
                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                        queue=mythic_container.PT_BUILD_RESPONSE_ROUTING_KEY,
                        body={"status": "error", "build_stderr": f"{traceback.format_exc()}\n{b}",
                              "uuid": msgDict["uuid"]}
                    )

    except Exception as e:
        logger.exception(f"[-] Failed to process build request")
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_BUILD_RESPONSE_ROUTING_KEY,
            body={"status": "error", "build_stderr": f"{traceback.format_exc()}\n{e}"}
        )


async def onNewCallback(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["payload_type"]:
                agent_builder = pt.__class__()
                try:
                    callbackData = mythic_container.MythicCommandBase.PTOnNewCallbackAllData(**msgDict)
                    callback_response = await agent_builder.on_new_callback(callbackData)
                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                        queue=mythic_container.PT_ON_NEW_CALLBACK_RESPONSE_ROUTING_KEY,
                        body=callback_response.to_json()
                    )
                except Exception as b:
                    logger.exception(f"[-] Failed to process on_new_callback for agent {pt.name}")
                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                        queue=mythic_container.PT_ON_NEW_CALLBACK_RESPONSE_ROUTING_KEY,
                        body={"success": False, "error": f"{traceback.format_exc()}\n{b}",
                              "agent_callback_id": msgDict["callback"]["agent_callback_id"]}
                    )
    except Exception as e:
        logger.exception(f"[-] Failed to process on_new_callback request")
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_ON_NEW_CALLBACK_RESPONSE_ROUTING_KEY,
            body={"success": False, "build_stderr": f"{traceback.format_exc()}\n{e}"}
        )


async def checkIfCallbacksAlive(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["container_name"]:
                agent_builder = pt.__class__()
                try:
                    callbackData = mythic_container.MythicCommandBase.PTCheckIfCallbacksAliveMessage(**msgDict)
                    callback_response = await agent_builder.check_if_callbacks_alive(callbackData)
                    return ujson.dumps(callback_response.to_json()).encode()
                except Exception as b:
                    logger.exception(f"[-] Failed to process check_if_callbacks_alive for agent {pt.name}")
                    response = {"success": False, "error": f"{traceback.format_exc()}\n{b}"}
                    return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        logger.exception(f"[-] Failed to process check_if_callbacks_alive request")
        response = {"success": False, "error": f"{traceback.format_exc()}\n{e}"}
        return ujson.dumps(response).encode()


async def initialize_task(
        command_class: MythicCommandBase.CommandBase,
        message_json: dict,
        error_routing_key: str
) -> MythicCommandBase.MythicTask:
    try:
        task = MythicCommandBase.MythicTask(
            message_json["task"],
            args=command_class.argument_class(
                command_line=message_json["task"]["params"],
                tasking_location=message_json["task"]["tasking_location"],
                raw_command_line=message_json["task"]["original_params"],
                initial_parameter_group=message_json["task"]["parameter_group_name"],
                task_dictionary=message_json["task"],
            ),
            callback_info=message_json["callback"]
        )
        if error_routing_key == mythic_container.PT_TASK_OPSEC_PRE_CHECK_RESPONSE or \
                error_routing_key == mythic_container.PT_TASK_CREATE_TASKING_RESPONSE:
            # if tasking came from the command_line or an unknown source, call parse_arguments to deal with unknown text
            if hasattr(task.args, "parse_dictionary") and callable(task.args.parse_dictionary):
                # if we got tasking from a modal popup or from tab complete, then the task.args.command_line is a
                # dictionary
                try:
                    await task.args.parse_dictionary(ujson.loads(message_json["task"]["params"]))
                except Exception as parseError:
                    await task.args.parse_arguments()
            else:
                await task.args.parse_arguments()
        else:
            try:
                dictionary = ujson.loads(message_json["task"]["params"])
                task.args.load_args_from_dictionary(dictionary, add_unknown_args=True)
            except Exception as loadException:
                pass
        for arg in task.args.args:
            if arg.type == MythicCommandBase.ParameterType.TypedArray and callable(arg.typedarray_parse_function):
                if len(arg.value) > 0 and arg.value[0][0] == "":
                    resp = await arg.typedarray_parse_function(MythicCommandBase.PTRPCTypedArrayParseFunctionMessage(
                        command=command_class.cmd,
                        parameter_name=arg.name,
                        payload_type="",
                        callback=message_json["callback"]["id"],
                        input_array=[x[1] for x in arg.value]
                    ))
                    if resp is None:
                        raise Exception('failed to get anything back from typedarray_parse_function')
                    if not resp.Success:
                        raise Exception(resp.Error)
                    arg.value = resp.TypedArray
                elif len(arg.value) > 0 and isinstance(arg.value[0], str):
                    resp = await arg.typedarray_parse_function(MythicCommandBase.PTRPCTypedArrayParseFunctionMessage(
                        command=command_class.cmd,
                        parameter_name=arg.name,
                        payload_type="",
                        callback=message_json["callback"]["id"],
                        input_array=arg.value
                    ))
                    if resp is None:
                        raise Exception('failed to get anything back from typedarray_parse_function')
                    if not resp.Success:
                        raise Exception(resp.Error)
                    task.args.set_arg(arg.name, resp.TypedArray)

    except Exception as pa:
        message = {
            "task_id": message_json["task"]["id"],
            "message": f"[-] failed to parse arguments for {message_json['task']['command_name']}: {pa}\n"
                       + str(traceback.format_exc()),
        }
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=error_routing_key,
            body=message
        )
        logger.error(f"failed to parse arguments and hit exception: {pa}")
        return None
    try:
        if error_routing_key == mythic_container.PT_TASK_OPSEC_PRE_CHECK_RESPONSE or \
                error_routing_key == mythic_container.PT_TASK_CREATE_TASKING_RESPONSE:
            await task.args.verify_required_args_have_values()
            task.parameter_group_name = task.args.get_parameter_group_name()
    except Exception as va:
        logger.error(f"failed to verify args have values and hit exception: {va}")
        message = {
            "task_id": message_json["task"]["id"],
            "message": f"[-] {message_json['task']['command_name']} has arguments with invalid values: {va} \n"
                       + str(traceback.format_exc()),
        }
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=error_routing_key,
            body=message
        )
        return None
    return task


async def verifyTaskArgs(
        task: MythicCommandBase.PTTaskMessageAllData,
        error_routing_key: str = ""
) -> bool:
    try:
        # if tasking came from the command_line or an unknown source, call parse_arguments to deal with unknown text
        if error_routing_key == mythic_container.PT_TASK_OPSEC_PRE_CHECK_RESPONSE or \
                error_routing_key == mythic_container.PT_TASK_CREATE_TASKING_RESPONSE:
            if hasattr(task.args, "parse_dictionary") and callable(task.args.parse_dictionary):
                try:
                    await task.args.parse_dictionary(ujson.loads(task.Task.Params))
                except Exception as parsingError:
                    await task.args.parse_arguments()
            else:
                await task.args.parse_arguments()
        else:
            try:
                dictionary = ujson.loads(task.Task.Params)
                task.args.load_args_from_dictionary(dictionary, add_unknown_args=True)
            except Exception as loadException:
                # must be looking at a task that doesn't have JSON-based parameters
                pass
        for arg in task.args.args:
            if arg.type == MythicCommandBase.ParameterType.TypedArray and callable(arg.typedarray_parse_function):
                if len(arg.value) > 0 and arg.value[0][0] == "":
                    inputArray = [x[1] for x in arg.value]
                    resp = await arg.typedarray_parse_function(MythicCommandBase.PTRPCTypedArrayParseFunctionMessage(
                        command=task.Task.CommandName,
                        parameter_name=arg.name,
                        payload_type=task.PayloadType,
                        callback=task.Callback.ID,
                        input_array=inputArray,
                        command_payload_type=task.CommandPayloadType
                    ))
                    if resp is None:
                        raise Exception('failed to get anything back from typedarray_parse_function')
                    if not resp.Success:
                        raise Exception(resp.Error)
                    task.args.set_arg(arg.name, resp.TypedArray)
                elif len(arg.value) > 0 and isinstance(arg.value[0], str):
                    resp = await arg.typedarray_parse_function(MythicCommandBase.PTRPCTypedArrayParseFunctionMessage(
                        command=task.Task.CommandName,
                        parameter_name=arg.name,
                        payload_type=task.PayloadType,
                        callback=task.Callback.ID,
                        input_array=arg.value,
                        command_payload_type=task.CommandPayloadType
                    ))
                    if resp is None:
                        raise Exception('failed to get anything back from typedarray_parse_function')
                    if not resp.Success:
                        raise Exception(resp.Error)
                    task.args.set_arg(arg.name, resp.TypedArray)

    except Exception as pa:
        message = {
            "task_id": task.Task.ID,
            "error": f"[-] failed to parse arguments for {task.Task.CommandName}: {pa}\n"
                     + str(traceback.format_exc()),
        }
        if error_routing_key == "":
            logger.exception(f"{ujson.dumps(message, indent=4)}")
        else:
            await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                queue=error_routing_key,
                body=message
            )
        return False
    try:
        if error_routing_key == mythic_container.PT_TASK_OPSEC_PRE_CHECK_RESPONSE or \
                error_routing_key == mythic_container.PT_TASK_CREATE_TASKING_RESPONSE:
            await task.args.verify_required_args_have_values()
            task.parameter_group_name = task.args.get_parameter_group_name()
    except Exception as va:
        message = {
            "task_id": task.Task.ID,
            "error": f"[-] {task.Task.CommandName} has arguments with invalid values: {va} \n"
                     + str(traceback.format_exc()),
        }
        if error_routing_key == "":
            logger.exception(f"{ujson.dumps(message, indent=4)}")
        else:
            await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                queue=error_routing_key,
                body=message
            )
        return False

    return True


async def opsecPreCheck(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["command_payload_type"]:
                if pt.name not in MythicCommandBase.commands:
                    logger.error(f"[-] no commands for payload type, can't do opsec pre-check")
                else:
                    for cmd in MythicCommandBase.commands[pt.name]:
                        if cmd.cmd == msgDict["task"]["command_name"]:
                            taskData = MythicCommandBase.PTTaskMessageAllData(**msgDict, args=cmd.argument_class)
                            if not await verifyTaskArgs(taskData,
                                                        mythic_container.PT_TASK_OPSEC_PRE_CHECK_RESPONSE):
                                return
                            else:
                                try:
                                    response = await cmd.opsec_pre(taskData=taskData)
                                    response.TaskID = taskData.Task.ID

                                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                        queue=mythic_container.PT_TASK_OPSEC_PRE_CHECK_RESPONSE,
                                        body=response.to_json()
                                    )
                                    return
                                except Exception as opsecError:
                                    logger.exception(f"Failed to run opsec pre check: {opsecError}")
                                    response = MythicCommandBase.PTTTaskOPSECPreTaskMessageResponse(
                                        TaskID=msgDict["task"]["id"], Success=False, Error=str(traceback.format_exc())
                                    )
                                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                        queue=mythic_container.PT_TASK_OPSEC_PRE_CHECK_RESPONSE,
                                        body=response.to_json()
                                    )
                                    return
        response = MythicCommandBase.PTTTaskOPSECPreTaskMessageResponse(
            TaskID=msgDict["task"]["id"], Success=True, OpsecPreBlocked=False,
            OpsecPreMessage="Payload Type or Command not found, passing by default",
        )
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_TASK_OPSEC_PRE_CHECK_RESPONSE,
            body=response.to_json()
        )

        return
    except Exception as e:
        logger.exception(f"[-] Failed to process OPSEC request")
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_TASK_OPSEC_PRE_CHECK_RESPONSE,
            body={"status": "error", "error": f"{traceback.format_exc()}\n{e}"}
        )


async def opsecPostCheck(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["command_payload_type"]:
                if pt.name not in MythicCommandBase.commands:
                    logger.error(f"[-] no commands for payload type, can't do opsec post-check")
                else:
                    for cmd in MythicCommandBase.commands[pt.name]:
                        if cmd.cmd == msgDict["task"]["command_name"]:
                            taskData = MythicCommandBase.PTTaskMessageAllData(**msgDict, args=cmd.argument_class)
                            if not await verifyTaskArgs(taskData,
                                                        mythic_container.PT_TASK_OPSEC_POST_CHECK_RESPONSE):
                                return
                            try:
                                response = await cmd.opsec_post(taskData=taskData)
                                response.TaskID = taskData.Task.ID
                                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                    queue=mythic_container.PT_TASK_OPSEC_POST_CHECK_RESPONSE,
                                    body=response.to_json()
                                )
                                return
                            except Exception as opsecError:
                                logger.exception(f"Failed to run opsec post check: {opsecError}")
                                response = MythicCommandBase.PTTTaskOPSECPostTaskMessageResponse(
                                    TaskID=msgDict["task"]["id"], Success=False, Error=str(traceback.format_exc())
                                )
                                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                    queue=mythic_container.PT_TASK_OPSEC_POST_CHECK_RESPONSE,
                                    body=response.to_json()
                                )
                                return
        response = MythicCommandBase.PTTTaskOPSECPostTaskMessageResponse(
            TaskID=msgDict["task"]["id"], Success=True, OpsecPostBlocked=False,
            OpsecPostMessage="Payload Type or Command not found, passing by default",
        )
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_TASK_OPSEC_POST_CHECK_RESPONSE,
            body=response.to_json()
        )
        return
    except Exception as e:
        logger.exception(f"[-] Failed to process OPSEC request")
        response = MythicCommandBase.PTTTaskOPSECPostTaskMessageResponse(
            TaskID=0, Success=False, Error=str(traceback.format_exc()),
        )
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_TASK_OPSEC_POST_CHECK_RESPONSE,
            body=response.to_json()
        )


async def createTasking(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["command_payload_type"]:
                if pt.name not in MythicCommandBase.commands:
                    logger.error(f"[-] no commands for payload type, can't do create tasking")
                else:
                    for cmd in MythicCommandBase.commands[pt.name]:
                        if cmd.cmd == msgDict["task"]["command_name"]:
                            try:
                                if hasattr(cmd, "create_go_tasking"):
                                    taskData = mythic_container.MythicCommandBase.PTTaskMessageAllData(**msgDict,
                                                                                                       args=cmd.argument_class)
                                    if not await verifyTaskArgs(taskData,
                                                                mythic_container.PT_TASK_CREATE_TASKING_RESPONSE):
                                        return
                                    createTaskingResponse = await cmd.create_go_tasking(taskData)
                                    createTaskingResponse.Params = str(taskData.args)
                                    if createTaskingResponse.Stdout is None:
                                        createTaskingResponse.Stdout = await taskData.args.get_unused_args()
                                    else:
                                        createTaskingResponse.Stdout += await taskData.args.get_unused_args()
                                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                        queue=mythic_container.PT_TASK_CREATE_TASKING_RESPONSE,
                                        body=createTaskingResponse.to_json()
                                    )
                                    return
                                else:
                                    task = await initialize_task(cmd, msgDict,
                                                                 mythic_container.PT_TASK_CREATE_TASKING_RESPONSE)
                                    if task is None:
                                        print("task is none from initialize task")
                                        # we hit an error and already sent the response, just return
                                        return
                                    createTaskingResponse = await cmd.create_tasking(task=task)
                                    response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
                                        TaskID=msgDict["task"]["id"],
                                        Success=True,
                                        TaskStatus=str(createTaskingResponse.status),
                                        Params=str(createTaskingResponse.args),
                                        DisplayParams=str(createTaskingResponse.display_params),
                                        CommandName=task.command_name,
                                        Stdout=str(createTaskingResponse.stdout),
                                        Stderr=str(createTaskingResponse.stderr),
                                        Completed=createTaskingResponse.completed,
                                        ParameterGroupName=createTaskingResponse.args.get_parameter_group_name(),
                                        CompletionFunctionName=createTaskingResponse.completed_callback_function,
                                        TokenID=createTaskingResponse.token
                                    )
                                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                        queue=mythic_container.PT_TASK_CREATE_TASKING_RESPONSE,
                                        body=response.to_json()
                                    )
                                    return
                            except Exception as opsecError:
                                logger.exception(f"Failed to run create tasking: {opsecError}")
                                response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
                                    TaskID=msgDict["task"]["id"],
                                    Success=False,
                                    Error=f"{traceback.format_exc()}"
                                )
                                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                    queue=mythic_container.PT_TASK_CREATE_TASKING_RESPONSE,
                                    body=response.to_json()
                                )
                                return
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=msgDict["task"]["id"], Success=True,
            Error="Payload Type or Command not found, passing by default",
        )
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_TASK_CREATE_TASKING_RESPONSE,
            body=response.to_json()
        )
        return
    except Exception as e:
        logger.exception(f"[-] Failed to process create tasking request")
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=0,
            Error=f"{traceback.format_exc()}\n{e}",
            Success=False
        )
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_TASK_CREATE_TASKING_RESPONSE,
            body=response.to_json()
        )


async def completionFunction(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["task"]["command_payload_type"]:
                if pt.name not in MythicCommandBase.commands:
                    logger.error(f"[-] no commands for payload type, can't do completion function")
                else:
                    for cmd in MythicCommandBase.commands[pt.name]:
                        if cmd.cmd == msgDict["task"]["task"]["command_name"]:
                            completionFunctionInput = MythicCommandBase.PTTaskCompletionFunctionMessage(
                                args=cmd.argument_class, **msgDict)
                            if not await verifyTaskArgs(completionFunctionInput.TaskData,
                                                        mythic_container.PT_TASK_COMPLETION_FUNCTION_RESPONSE):
                                return
                            if completionFunctionInput.SubtaskData is not None:
                                for subcmd in MythicCommandBase.commands[pt.name]:
                                    if subcmd.cmd == completionFunctionInput.SubtaskData.Task.CommandName:
                                        completionFunctionInput.SubtaskData = MythicCommandBase.PTTaskMessageAllData(
                                            **msgDict["subtask"], args=subcmd.argument_class)
                                        if not await verifyTaskArgs(completionFunctionInput.SubtaskData,
                                                                    mythic_container.PT_TASK_COMPLETION_FUNCTION_RESPONSE):
                                            return
                                        break
                            try:
                                if completionFunctionInput.CompletionFunctionName in cmd.completion_functions:
                                    response = await cmd.completion_functions[
                                        completionFunctionInput.CompletionFunctionName](completionFunctionInput)
                                else:
                                    response = mythic_container.MythicCommandBase.PTTaskCompletionFunctionMessageResponse(
                                        Success=False,
                                        TaskID=msgDict["task"]["task"]["id"],
                                        ParentTaskId=0,
                                        Error=f"{completionFunctionInput.CompletionFunctionName} not in command's listed completion_functions - unable to call it"
                                    )
                                if completionFunctionInput.SubtaskData is not None:
                                    response.TaskID = completionFunctionInput.SubtaskData.Task.ID
                                    response.ParentTaskId = completionFunctionInput.TaskData.Task.ID
                                else:
                                    response.TaskID = completionFunctionInput.TaskData.Task.ID
                                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                    queue=mythic_container.PT_TASK_COMPLETION_FUNCTION_RESPONSE,
                                    body=response.to_json()
                                )
                                return
                            except Exception as completionException:
                                response = mythic_container.MythicCommandBase.PTTaskCompletionFunctionMessageResponse(
                                    Success=False,
                                    TaskID=msgDict["task"]["task"]["id"],
                                    ParentTaskId=0,
                                    Error=f"Failed to call completion function: {traceback.format_exc()}"
                                )
                                if "subtask" in msgDict and msgDict['subtask'] is not None:
                                    response.TaskID = msgDict['subtask']['task']['id']
                                    response.ParentTaskId = msgDict['task']['task']['id']
                                else:
                                    response.TaskID = msgDict['task']["task"]['id']
                                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                    queue=mythic_container.PT_TASK_COMPLETION_FUNCTION_RESPONSE,
                                    body=response.to_json()
                                )

    except Exception as e:
        logger.error(f"Failed to call completion function: {traceback.format_exc()}\n{e}")
        response = mythic_container.MythicCommandBase.PTTaskCompletionFunctionMessageResponse(
            Success=False,
            TaskID=0,
            ParentTaskId=0,
            Error=f"Failed to call completion function: {traceback.format_exc()}\n{e}"
        )
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_TASK_COMPLETION_FUNCTION_RESPONSE,
            body=response.to_json()
        )


async def processResponse(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["task"]["command_payload_type"]:
                if pt.name not in MythicCommandBase.commands:
                    logger.error(f"[-] no commands for payload type, can't do process response")
                else:
                    for cmd in MythicCommandBase.commands[pt.name]:
                        if cmd.cmd == msgDict["task"]["task"]["command_name"]:
                            taskData = MythicCommandBase.PTTaskMessageAllData(**msgDict["task"],
                                                                              args=cmd.argument_class)
                            try:
                                response = await cmd.process_response(task=taskData, response=msgDict["response"])
                                response.TaskID = taskData.Task.ID

                                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                    queue=mythic_container.PT_TASK_PROCESS_RESPONSE_RESPONSE,
                                    body=response.to_json()
                                )
                                return
                            except Exception as opsecError:
                                logger.exception(f"Failed to run process response: {opsecError}")
                                response = MythicCommandBase.PTTaskProcessResponseMessageResponse(
                                    TaskID=msgDict["task"]["task"]["id"], Success=False,
                                    Error=str(traceback.format_exc())
                                )
                                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                                    queue=mythic_container.PT_TASK_PROCESS_RESPONSE_RESPONSE,
                                    body=response.to_json()
                                )
                                return
        response = MythicCommandBase.PTTaskProcessResponseMessageResponse(
            TaskID=msgDict["task"]["task"]["id"], Success=False, Error="Failed to find command"
        )
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_TASK_PROCESS_RESPONSE_RESPONSE,
            body=response.to_json()
        )

        return
    except Exception as e:
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.PT_TASK_PROCESS_RESPONSE_RESPONSE,
            body={"status": "error", "error": f"{traceback.format_exc()}\n{e}"}
        )


async def dynamicQueryFunction(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["command_payload_type"]:
                if pt.name not in MythicCommandBase.commands:
                    logger.error(f"[-] no commands for payload type, can't do dynamic query function")
                else:
                    for cmd in MythicCommandBase.commands[pt.name]:
                        if cmd.cmd == msgDict["command"]:
                            if cmd.argument_class is not None:
                                for param in cmd.argument_class(command_line="").args:
                                    if param.name == msgDict["parameter_name"]:
                                        if callable(param.dynamic_query_function):
                                            try:
                                                result = await param.dynamic_query_function(
                                                    mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessage(
                                                        **msgDict))
                                            except Exception as callEx:
                                                logger.exception(
                                                    f"Failed to call dynamic query function for {cmd.cmd}")
                                                result = mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse(
                                                    Success=False,
                                                    Error=f"Failed to call dynamic query function: {traceback.format_exc()}"
                                                )
                                                return ujson.dumps(result.to_json()).encode()
                                            if result is None:
                                                response = mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse(
                                                    Success=False,
                                                    Error=f"Failed to call dynamic query function: No result returned"
                                                )
                                                return ujson.dumps(response.to_json()).encode()
                                            elif isinstance(result, list):
                                                response = mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse(
                                                    Success=True,
                                                    Choices=result
                                                )
                                                return ujson.dumps(response.to_json()).encode()
                                            elif isinstance(result,
                                                            mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse):
                                                return ujson.dumps(result.to_json()).encode()
                                            else:
                                                response = mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse(
                                                    Success=False,
                                                    Error=f"unknown result type from function: {result}"
                                                )
                                                return ujson.dumps(response.to_json()).encode()
                                        else:
                                            logger.error(f"dynamic query function for {cmd.cmd} isn't callable")
                                            response = mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse(
                                                Success=False,
                                                Error=f"dynamic query function for {cmd.cmd} isn't callable"
                                            )
                                            return ujson.dumps(response.to_json()).encode()
                                response = mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse(
                                    Success=False,
                                    Error=f"Failed to find parameter name for dynamic query function: {msgDict['parameter_name']}"
                                )
                                return ujson.dumps(response.to_json()).encode()
                            else:
                                response = mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse(
                                    Success=False,
                                    Error=f"No argument class for command {cmd.cmd}"
                                )
                                return ujson.dumps(response.to_json()).encode()
                    response = mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse(
                        Success=False,
                        Error=f"Failed to find command, {msgDict['command']}"
                    )
                    return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.MythicCommandBase.PTRPCDynamicQueryFunctionMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call dynamic query function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def typedTaskParseFunction(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["command_payload_type"]:
                if pt.name not in MythicCommandBase.commands:
                    logger.error(f"[-] no commands for payload type, can't do typedarray parse function")
                else:
                    for cmd in MythicCommandBase.commands[pt.name]:
                        if cmd.cmd == msgDict["command"]:
                            if cmd.argument_class is not None:
                                for param in cmd.argument_class(command_line="").args:
                                    if param.name == msgDict["parameter_name"]:
                                        if callable(param.typedarray_parse_function):
                                            try:
                                                result = await param.typedarray_parse_function(
                                                    mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessage(
                                                        **msgDict))
                                            except Exception as callEx:
                                                logger.exception(
                                                    f"Failed to call typedarray parse function for {cmd.cmd}")
                                                result = mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse(
                                                    Success=False,
                                                    Error=f"Failed to call typedarray parse function: {traceback.format_exc()}"
                                                )
                                                return ujson.dumps(result.to_json()).encode()
                                            if result is None:
                                                response = mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse(
                                                    Success=False,
                                                    Error=f"Failed to call typedarray parse function: No result returned"
                                                )
                                                return ujson.dumps(response.to_json()).encode()
                                            elif isinstance(result, list):
                                                response = mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse(
                                                    Success=True,
                                                    TypedArray=result
                                                )
                                                return ujson.dumps(response.to_json()).encode()
                                            elif isinstance(result,
                                                            mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse):
                                                return ujson.dumps(result.to_json()).encode()
                                            else:
                                                response = mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse(
                                                    Success=False,
                                                    Error=f"unknown result type from function: {result}"
                                                )
                                                return ujson.dumps(response.to_json()).encode()
                                        else:
                                            logger.error(f"typedarray parse function for {cmd.cmd} isn't callable")
                                            response = mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse(
                                                Success=False,
                                                Error=f"typedarray parse function for {cmd.cmd} isn't callable"
                                            )
                                            return ujson.dumps(response.to_json()).encode()
                                response = mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse(
                                    Success=False,
                                    Error=f"Failed to find parameter name for typedarray parse function: {msgDict['parameter_name']}"
                                )
                                return ujson.dumps(response.to_json()).encode()
                            else:
                                response = mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse(
                                    Success=False,
                                    Error=f"No argument class for command {cmd.cmd}"
                                )
                                return ujson.dumps(response.to_json()).encode()
                    response = mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse(
                        Success=False,
                        Error=f"Failed to find command, {msgDict['command']}"
                    )
                    return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.MythicCommandBase.PTRPCTypedArrayParseFunctionMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call typedarray parse function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def customRPCFunction(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        incomingMessage = PayloadBuilder.PTOtherServiceRPCMessage(**msgDict)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == incomingMessage.ServiceName:
                if pt.custom_rpc_functions is not None:
                    for key, f in pt.custom_rpc_functions.items():
                        if key == incomingMessage.ServiceRPCFunction:
                            response = await f(incomingMessage)
                            return ujson.dumps(response.to_json()).encode()
                    response = PayloadBuilder.PTOtherServiceRPCMessageResponse(
                        Success=False,
                        Error=f"Failed to find function {incomingMessage.ServiceRPCFunction} in custom rpc functions for {pt.name}"
                    )
                    return ujson.dumps(response.to_json()).encode()
                else:
                    response = PayloadBuilder.PTOtherServiceRPCMessageResponse(
                        Success=False,
                        Error=f"No custom rpc functions defined for payload {pt.name}"
                    )
                    return ujson.dumps(response.to_json()).encode()
        response = mythic_container.PayloadBuilder.PTOtherServiceRPCMessageResponse(
            Success=False,
            Error=f"Failed to find service: {incomingMessage.ServiceName}"
        )
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.PayloadBuilder.PTOtherServiceRPCMessageResponse(
            Success=False,
            Error=f"Failed to call custom RPC function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def RunCommandWithTimeout(command: str, cwd: str, timeoutSeconds: int) -> (bytes, bytes, int):
    proc = await asyncio.create_subprocess_shell(command,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE,
                                                 cwd=cwd)
    task = asyncio.Task(proc.communicate())
    done, pending = await asyncio.wait([task], timeout=timeoutSeconds)
    if pending:
        print("timeout!", task._state)
    stdout, stderr = await task  # Note: It is OK to await a task more than once
    return stdout, stderr, proc.returncode


async def reSyncPayloadType(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in PayloadBuilder.payloadTypes.items():
            if pt.name == msgDict["payload_type"]:
                mythic_container.MythicCommandBase.commands.pop(pt.name, None)
                await mythic_container.mythic_service.syncPayloadData(pt)
                return ujson.dumps({"success": True}).encode()
        return ujson.dumps({"success": False, "error": "Failed to find payload type"}).encode()
    except Exception as e:
        logger.exception(f"Failed to re-sync payload type: {e}")
        return ujson.dumps({"success": False, "error": f"Failed to sync: {traceback.format_exc()}\n{e}"}).encode()
