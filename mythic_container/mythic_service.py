#!/usr/bin/env python3
import sys
import json
import asyncio
import mythic_container
from . import MythicCommandBase
from . import PayloadBuilder
from .logging import logger, initialize
from . import agent_utils
from . import MythicGoRPC
from . import C2ProfileBase
from . import c2_utils
from . import TranslationBase
from . import WebhookBase
from . import LoggingBase
from . import webhook_utils
from . import logging_utils
from .rabbitmq import failedConnectRetryDelay

# set the global hostname variable
output = ""


# start our service
def start_and_run_forever():
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_services())
        loop.run_forever()
        logger.error("start_and_run_forever finished")
    except KeyboardInterrupt:
        sys.exit(0)


def getRoutingKey(containerName: str, baseKey: str) -> str:
    return f"{containerName}_{baseKey}"


def getWebhookRoutingKey(webhookType: str) -> str:
    return f"{mythic_container.EMIT_WEBHOOK_ROUTING_KEY_PREFIX}.{webhookType}"


def getLoggingRoutingKey(loggingType: str) -> str:
    return f"{mythic_container.EMIT_LOG_ROUTING_KEY_PREFIX}.{loggingType}"


payloadQueueTasks = []


async def startPayloadRabbitMQ(pt: PayloadBuilder.PayloadType) -> None:
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(pt.name, mythic_container.PAYLOAD_BUILD_ROUTING_KEY),
        routing_key=getRoutingKey(pt.name, mythic_container.PAYLOAD_BUILD_ROUTING_KEY),
        handler=agent_utils.buildWrapper
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(pt.name, mythic_container.PT_TASK_OPSEC_PRE_CHECK),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_TASK_OPSEC_PRE_CHECK),
        handler=agent_utils.opsecPreCheck
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(pt.name, mythic_container.PT_TASK_CREATE_TASKING),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_TASK_CREATE_TASKING),
        handler=agent_utils.createTasking
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(pt.name, mythic_container.PT_TASK_OPSEC_POST_CHECK),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_TASK_OPSEC_POST_CHECK),
        handler=agent_utils.opsecPostCheck
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(pt.name, mythic_container.PT_TASK_PROCESS_RESPONSE),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_TASK_PROCESS_RESPONSE),
        handler=agent_utils.processResponse
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(pt.name, mythic_container.PT_TASK_COMPLETION_FUNCTION),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_TASK_COMPLETION_FUNCTION),
        handler=agent_utils.completionFunction
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(pt.name, mythic_container.PT_RPC_COMMAND_DYNAMIC_QUERY_FUNCTION),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_RPC_COMMAND_DYNAMIC_QUERY_FUNCTION),
        handler=agent_utils.dynamicQueryFunction
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(pt.name, mythic_container.MYTHIC_RPC_OTHER_SERVICES_RPC),
        routing_key=getRoutingKey(pt.name, mythic_container.MYTHIC_RPC_OTHER_SERVICES_RPC),
        handler=agent_utils.customRPCFunction
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(pt.name, mythic_container.PT_RPC_RESYNC_ROUTING_KEY),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_RPC_RESYNC_ROUTING_KEY),
        handler=agent_utils.reSyncPayloadType
    )))


async def syncPayloadData(pt: PayloadBuilder.PayloadType) -> None:
    syncMessage = {
        "payload_type": pt.to_json(),
        "commands": [],
        "container_version": mythic_container.containerVersion
    }

    modulePieces = pt.__module__.split(".")
    modulePrefix = ".".join(modulePieces[:-1])
    for cls in MythicCommandBase.CommandBase.__subclasses__():
        if cls.__module__.startswith(modulePrefix):
            logger.info(f"[*] Processing command {cls.cmd}")
            if pt.name not in MythicCommandBase.commands:
                MythicCommandBase.commands[pt.name] = []
            MythicCommandBase.commands[pt.name].append(
                cls(pt.agent_path, pt.agent_code_path, pt.agent_browserscript_path))
            syncMessage["commands"].append(
                cls(pt.agent_path, pt.agent_code_path, pt.agent_browserscript_path).to_json())
    while True:
        response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
            queue=mythic_container.PT_SYNC_ROUTING_KEY,
            body=syncMessage)
        if response is None:
            logger.error("[-] Failed to get a response back from syncing RPC message, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif "success" not in response:
            logger.error("[-] RPC response doesn't contain success, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif not response["success"]:
            logger.error(f"[-] Failed to sync {pt.name}: {response['error']}, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        else:
            logger.info(f"[+] Successfully synced {pt.name}")
            return


async def startC2RabbitMQ(c2: C2ProfileBase.C2Profile) -> None:
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_START_SERVER_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_START_SERVER_ROUTING_KEY),
        handler=c2_utils.startServer
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_CONFIG_CHECK_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_CONFIG_CHECK_ROUTING_KEY),
        handler=c2_utils.configChecks
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_GET_SERVER_DEBUG_OUTPUT),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_GET_SERVER_DEBUG_OUTPUT),
        handler=c2_utils.getDebugOutput
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_GET_FILE),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_GET_FILE),
        handler=c2_utils.getFile
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_REDIRECTOR_RULES_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_REDIRECTOR_RULES_ROUTING_KEY),
        handler=c2_utils.getRedirectorRules
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_LIST_FILE),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_LIST_FILE),
        handler=c2_utils.listFile
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_OPSEC_CHECKS_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_OPSEC_CHECKS_ROUTING_KEY),
        handler=c2_utils.opsecChecks
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_REMOVE_FILE),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_REMOVE_FILE),
        handler=c2_utils.removeFile
    )))

    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_STOP_SERVER_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_STOP_SERVER_ROUTING_KEY),
        handler=c2_utils.stopServer
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_WRITE_FILE),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_WRITE_FILE),
        handler=c2_utils.writeFile
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.MYTHIC_RPC_OTHER_SERVICES_RPC),
        routing_key=getRoutingKey(c2.name, mythic_container.MYTHIC_RPC_OTHER_SERVICES_RPC),
        handler=c2_utils.customRPCFunction
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_RESYNC_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_RESYNC_ROUTING_KEY),
        handler=c2_utils.reSyncC2Profile
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_GET_IOC_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_GET_IOC_ROUTING_KEY),
        handler=c2_utils.getIOC
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_SAMPLE_MESSAGE_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_SAMPLE_MESSAGE_ROUTING_KEY),
        handler=c2_utils.sampleMessage
    )))


async def syncC2ProfileData(c2: C2ProfileBase.C2Profile) -> None:
    syncMessage = {
        **c2.to_json(),
        "container_version": mythic_container.containerVersion
    }

    while True:
        response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
            queue=mythic_container.C2_SYNC_ROUTING_KEY,
            body=syncMessage)
        if response is None:
            logger.error("[-] Failed to get a response back from syncing RPC message, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif "success" not in response:
            logger.error("[-] RPC response doesn't contain success, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif not response["success"]:
            logger.error(f"[-] Failed to sync {c2.name}: {response['error']}, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        else:
            logger.info(f"[+] Successfully synced {c2.name}")
            return


async def startTranslatorRabbitMQ(tr: TranslationBase.TranslationContainer) -> None:
    payloadQueueTasks.append(asyncio.create_task(TranslationBase.handleTranslationServices(tr.name)))


async def syncTranslatorData(tr: TranslationBase.TranslationContainer) -> None:
    syncMessage = {
        **tr.to_json(),
        "container_version": mythic_container.containerVersion
    }
    while True:
        response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
            queue=mythic_container.TR_SYNC_ROUTING_KEY,
            body=syncMessage)
        if response is None:
            logger.error("[-] Failed to get a response back from syncing RPC message, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif "success" not in response:
            logger.error("[-] RPC response doesn't contain success, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif not response["success"]:
            logger.error(f"[-] Failed to sync {tr.name}: {response['error']}, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        else:
            logger.info(f"[+] Successfully synced {tr.name}")
            return


async def syncWebhookData(wb: WebhookBase.Webhook) -> None:
    if wb.new_startup is not None and callable(wb.new_startup):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_STARTUP),
                routing_key=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_STARTUP),
                handler=webhook_utils.new_startup
            )))
    if wb.new_callback is not None and callable(wb.new_callback):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_CALLBACK),
                routing_key=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_CALLBACK),
                handler=webhook_utils.new_callback
            )))
    if wb.new_feedback is not None and callable(wb.new_feedback):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_FEEDBACK),
                routing_key=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_FEEDBACK),
                handler=webhook_utils.new_feedback
            )))
    if wb.new_alert is not None and callable(wb.new_alert):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_ALERT),
                routing_key=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_ALERT),
                handler=webhook_utils.new_alert
            )))
    if wb.new_custom is not None and callable(wb.new_custom):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_CUSTOM),
                routing_key=getWebhookRoutingKey(mythic_container.WEBHOOK_TYPE_NEW_CUSTOM),
                handler=webhook_utils.new_custom
            )))
    logger.info(f"Successfully started webhook service")


async def syncLoggingData(wb: LoggingBase.Log) -> None:
    if wb.new_callback is not None and callable(wb.new_callback):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getLoggingRoutingKey(mythic_container.LOG_TYPE_CALLBACK),
                routing_key=getLoggingRoutingKey(mythic_container.LOG_TYPE_CALLBACK),
                handler=logging_utils.new_callback
            )))
    if wb.new_credential is not None and callable(wb.new_credential):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getLoggingRoutingKey(mythic_container.LOG_TYPE_CREDENTIAL),
                routing_key=getLoggingRoutingKey(mythic_container.LOG_TYPE_CREDENTIAL),
                handler=logging_utils.new_credential
            )))
    if wb.new_keylog is not None and callable(wb.new_keylog):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getLoggingRoutingKey(mythic_container.LOG_TYPE_KEYLOG),
                routing_key=getLoggingRoutingKey(mythic_container.LOG_TYPE_KEYLOG),
                handler=logging_utils.new_keylog
            )))
    if wb.new_file is not None and callable(wb.new_file):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getLoggingRoutingKey(mythic_container.LOG_TYPE_FILE),
                routing_key=getLoggingRoutingKey(mythic_container.LOG_TYPE_FILE),
                handler=logging_utils.new_file
            )))
    if wb.new_payload is not None and callable(wb.new_payload):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getLoggingRoutingKey(mythic_container.LOG_TYPE_PAYLOAD),
                routing_key=getLoggingRoutingKey(mythic_container.LOG_TYPE_PAYLOAD),
                handler=logging_utils.new_payload
            )))
    if wb.new_artifact is not None and callable(wb.new_artifact):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getLoggingRoutingKey(mythic_container.LOG_TYPE_ARTIFACT),
                routing_key=getLoggingRoutingKey(mythic_container.LOG_TYPE_ARTIFACT),
                handler=logging_utils.new_artifact
            )))
    if wb.new_task is not None and callable(wb.new_task):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getLoggingRoutingKey(mythic_container.LOG_TYPE_TASK),
                routing_key=getLoggingRoutingKey(mythic_container.LOG_TYPE_TASK),
                handler=logging_utils.new_task
            )))

    logger.info(f"Successfully started logging service")


consumingServices = []


async def start_services():
    initialize()

    logger.info(
        f"[+] Starting Services with version {mythic_container.containerVersion} and PyPi version {mythic_container.PyPi_version}\n")
    webhook_services = WebhookBase.Webhook.__subclasses__()
    for cls in webhook_services:
        logger.info(f"[*] Processing webhook service")
        webhook = cls()
        consumingServices.append(webhook)
        await syncWebhookData(webhook)
    logging_services = LoggingBase.Log.__subclasses__()
    for cls in logging_services:
        logger.info(f"[*] Processing logging services")
        definedLog = cls()
        consumingServices.append(definedLog)
        await syncLoggingData(definedLog)
    payloadTypes = PayloadBuilder.PayloadType.__subclasses__()
    for cls in payloadTypes:
        payload_type = cls()
        if payload_type.name in PayloadBuilder.payloadTypes:
            logger.error(f"[-] attempting to import {payload_type.name} multiple times - probably due to import issues")
            continue
        PayloadBuilder.payloadTypes[payload_type.name] = payload_type
        logger.info(f"[*] Processing agent: {payload_type.name}")
        await syncPayloadData(payload_type)
        await startPayloadRabbitMQ(payload_type)

    c2Profiles = C2ProfileBase.C2Profile.__subclasses__()
    for cls in c2Profiles:
        c2profile = cls()
        if c2profile.name in C2ProfileBase.c2Profiles:
            logger.error(f"[-] attempting to import {c2profile.name} multiple times - probably due to import issues")
            continue
        C2ProfileBase.c2Profiles[c2profile.name] = c2profile
        logger.info(f"[*] Processing c2 profile: {c2profile.name}")
        await startC2RabbitMQ(c2profile)
        await syncC2ProfileData(c2profile)

    translation_services = TranslationBase.TranslationContainer.__subclasses__()
    for cls in translation_services:
        translator = cls()
        if translator.name in TranslationBase.translationServices:
            logger.error(f"[-] attempting to import {translator.name} multiple times - probably due to import issues")
            continue
        TranslationBase.translationServices[translator.name] = translator
        logger.info(f"[*] Processing translation service: {translator.name}")
        await syncTranslatorData(translator)
        await startTranslatorRabbitMQ(translator)

    logger.info("[+] All services synced with Mythic!")
    logger.info("[*] Starting services to listen...")


async def test_command(payload_type_name: str,
                       command_name: str,
                       operation_name: str = None,
                       task_id: int = None,
                       tasking_location: str = "command_line",
                       parameters_string: str = None,
                       parameters_dictionary: dict = None):
    logger.info(f"[*] Started testing {payload_type_name}'s {command_name} command")
    if operation_name is None or task_id is None:
        logger.info(f"[*] Specify an operation_name and task_id to get real data for testing."
                    f"\nThis does not adjust your specified command/parameters, but allows MythicRPC calls to work properly")
    params = parameters_string
    if parameters_dictionary is not None:
        params = json.dumps(parameters_dictionary)
    payloadTypes = PayloadBuilder.PayloadType.__subclasses__()
    for cls in payloadTypes:
        payload_type = cls()
        if payload_type.name == payload_type_name:
            logger.info(f"[+] Found payload type: {payload_type.name}")
            modulePieces = payload_type.__module__.split(".")
            modulePrefix = ".".join(modulePieces[:-1])
            for cmdcls in MythicCommandBase.CommandBase.__subclasses__():
                if cmdcls.__module__.startswith(modulePrefix):
                    if cmdcls.cmd == command_name:
                        commandInstance = cmdcls(payload_type.agent_path, payload_type.agent_code_path,
                                                 payload_type.agent_browserscript_path)
                        logger.info(f"[+] Found command: {commandInstance.cmd}")
                        opsecPre = MythicCommandBase.PTTaskMessageAllData(
                            task={
                                "tasking_location": tasking_location,
                                "params": params,
                                "original_params": params
                            },
                            payload_type=payload_type_name,
                            args=cmdcls.argument_class
                        )
                        opsecPost = MythicCommandBase.PTTaskMessageAllData(
                            task={
                                "tasking_location": tasking_location,
                                "params": params,
                                "original_params": params
                            },
                            args=cmdcls.argument_class
                        )
                        createTasking = MythicCommandBase.PTTaskMessageAllData(
                            task={
                                "tasking_location": tasking_location,
                                "params": params,
                                "original_params": params
                            },
                            args=cmdcls.argument_class
                        )
                        if operation_name is None or task_id is None:
                            logger.info(
                                f"[*] operation_name is None, testing with fake data. Some MythicRPC functions might not work")
                        else:
                            logger.info(f"[*] Fetching information for task {task_id} of operation {operation_name}")
                            fetchResp = await MythicGoRPC.SendMythicRPCTaskDisplayToRealIdSearch(
                                MythicGoRPC.MythicRPCTaskDisplayToRealIdSearchMessage(
                                    TaskDisplayID=task_id,
                                    OperationName=operation_name
                                ))
                            if not fetchResp.Success:
                                logger.error(f"[-] Failed to find task: {fetchResp.Error}")
                                sys.exit(1)
                            else:
                                taskResp = await MythicGoRPC.SendMythicRPCTaskSearch(
                                    MythicGoRPC.MythicRPCTaskSearchMessage(
                                        TaskID=fetchResp.TaskID,
                                    ))
                                if not taskResp.Success:
                                    logger.error(f"[-] Failed to get task information: {taskResp.Error}")
                                    sys.exit(1)
                                elif len(taskResp.Tasks) == 0:
                                    logger.error(f"[-] Failed to search for task information")
                                    sys.exit(1)
                                else:
                                    opsecPre.Task = MythicCommandBase.PTTaskMessageTaskData(
                                        **taskResp.Tasks[0].to_json())
                                    opsecPre.Task.CommandName = command_name
                                    opsecPre.Task.Params = params
                                    opsecPre.Task.OriginalParams = params
                                    opsecPre.Task.TaskingLocation = tasking_location
                                    opsecPost.Task = MythicCommandBase.PTTaskMessageTaskData(
                                        **taskResp.Tasks[0].to_json())
                                    opsecPost.Task.CommandName = command_name
                                    opsecPost.Task.Params = params
                                    opsecPost.Task.OriginalParams = params
                                    opsecPost.Task.TaskingLocation = tasking_location
                                    createTasking.Task = MythicCommandBase.PTTaskMessageTaskData(
                                        **taskResp.Tasks[0].to_json())
                                    createTasking.Task.CommandName = command_name
                                    createTasking.Task.Params = params
                                    createTasking.Task.OriginalParams = params
                                    createTasking.Task.TaskingLocation = tasking_location
                        logger.info(f"[*] Testing OPSEC PRE")
                        if not await agent_utils.verifyTaskArgs(opsecPre, ""):
                            return
                        else:
                            try:
                                response = await commandInstance.opsec_pre(taskData=opsecPre)
                                logger.info(f"[+] Finished OPSEC PRE:\n{json.dumps(response.to_json(), indent=4)}")
                            except Exception as e:
                                logger.exception(f"[*] Hit exception: {e}")
                        logger.info(f"[*] Testing Create Tasking")
                        task = await agent_utils.initialize_task(commandInstance, {
                            "task": createTasking.Task.to_json(),
                            "callback": createTasking.Callback.to_json()
                        }, "")
                        if task is None:
                            # we hit an error and already sent the response, just return
                            return
                        else:
                            try:
                                if hasattr(commandInstance, "create_go_tasking"):
                                    if not await agent_utils.verifyTaskArgs(createTasking, ""):
                                        return
                                    createTaskingResponse = await commandInstance.create_go_tasking(
                                        taskData=createTasking)
                                    if createTaskingResponse.Params is None:
                                        # no manual args were set, so parse them from the task.args
                                        createTaskingResponse.Params = str(task.args)
                                    logger.info(
                                        f"[+] Finished Create Tasking (new):\n{json.dumps(createTaskingResponse.to_json(), indent=4)}")
                                else:
                                    createTaskingResponse = await commandInstance.create_tasking(task=task)
                                    logger.info(
                                        f"[+] Finished Create Tasking (legacy):\n{json.dumps(createTaskingResponse.to_json(), indent=4)}")
                            except Exception as createTaskingException:
                                logger.exception(f"[*] Hit exception: {createTaskingException}")
                        logger.info(f"[*] Testing OPSEC Post")
                        if not await agent_utils.verifyTaskArgs(opsecPost, ""):
                            return
                        else:
                            try:
                                response = await commandInstance.opsec_post(taskData=opsecPost)
                                logger.info(f"[+] Finished OPSEC POST:\n{json.dumps(response.to_json(), indent=4)}")
                            except Exception as e:
                                logger.exception(f"[*] Hit exception: {e}")
                        return
            logger.error(f"[-] Failed to find command: {command_name}")
    logger.error(f"[-] Failed to find payload type: {payload_type_name}")
