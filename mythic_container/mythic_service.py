#!/usr/bin/env python3
import sys
import json
import ujson
import os
import traceback
import pathlib
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
from . import AuthBase
from . import auth_utils
from . import EventingBase
from . import eventing_utils
from .rabbitmq import failedConnectRetryDelay


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


# Shared file based functionality for all services
async def listFile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["container_name"]:
                response = listFilesOfPath(c2.server_folder_path)
                return ujson.dumps(response.to_json()).encode()
        # if it's not a c2 profile, then just use the current path of the script that's executing
        response = listFilesOfPath(os.path.dirname(os.path.abspath(sys.argv[0])))
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.SharedClasses.ListFileMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call list file function function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


def listFilesOfPath(path: str) -> mythic_container.SharedClasses.ListFileMessageResponse:
    response = mythic_container.SharedClasses.ListFileMessageResponse(Success=False)
    try:
        files = os.listdir(path)
        files = [f for f in files if os.path.isfile(pathlib.Path(path) / f)]
        response.Files = files
        response.Success = True
    except Exception as e:
        response.Error = f"{traceback.format_exc()}\n{e}"
    return response


async def removeFile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        inputMsg = mythic_container.SharedClasses.RemoveFileMessage(**msgDict)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["container_name"]:
                response = removeFileOfPath(c2.server_folder_path / inputMsg.Filename)
                return ujson.dumps(response.to_json()).encode()
        path = pathlib.Path(os.path.dirname(os.path.abspath(sys.argv[0]))) / inputMsg.Filename
        response = removeFileOfPath(path)
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.SharedClasses.GetFileMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get removeFile function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


def removeFileOfPath(path: str) -> mythic_container.SharedClasses.RemoveFileMessageResponse:
    response = mythic_container.SharedClasses.RemoveFileMessageResponse(Success=False)
    try:
        path = path.resolve()
        os.remove(path)
        response.Success = True
    except Exception as e:
        response.Error = f"{traceback.format_exc()}\n{e}"
    return response


async def getFile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        inputMsg = mythic_container.SharedClasses.GetFileMessage(**msgDict)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["container_name"]:
                response = getFileOfPath(c2.server_folder_path / inputMsg.Filename)
                return ujson.dumps(response.to_json()).encode()
        path = pathlib.Path(os.path.dirname(os.path.abspath(sys.argv[0]))) / inputMsg.Filename
        response = getFileOfPath(path)
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.SharedClasses.GetFileMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get file function function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


def getFileOfPath(path: str) -> mythic_container.SharedClasses.GetFileMessageResponse:
    response = mythic_container.SharedClasses.GetFileMessageResponse(Success=False)
    try:
        file_data = open(path, "rb").read()
        response.Success = True
        response.Message = file_data
    except Exception as e:
        response.Error = f"{traceback.format_exc()}\n{e}"
    return response


async def writeFile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        inputMsg = mythic_container.SharedClasses.WriteFileMessage(**msgDict)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["container_name"]:
                response = writeFileOfPath(c2.server_folder_path / inputMsg.Filename, inputMsg.Contents)
                return ujson.dumps(response.to_json()).encode()
        path = pathlib.Path(os.path.dirname(os.path.abspath(sys.argv[0]))) / inputMsg.Filename
        response = writeFileOfPath(path, inputMsg.Contents)
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        logger.exception(f"[-] Failed to write to file with exception: {e}")
        response = mythic_container.SharedClasses.WriteFileMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call write file function function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


def writeFileOfPath(path: str, bytesToWrite: bytes) -> mythic_container.SharedClasses.WriteFileMessageResponse:
    response = mythic_container.SharedClasses.WriteFileMessageResponse(Success=False)
    try:
        with open(path, "wb") as f:
            f.write(bytesToWrite)
        response.Success = True
        response.Message = "Successfully wrote file"
    except Exception as e:
        logger.exception(f"[-] Failed to write to file: {e}")
        response.Error = f"{traceback.format_exc()}\n{e}"
    return response


async def onStart(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        inputMsg = mythic_container.SharedClasses.ContainerOnStartMessage(**msgDict)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == inputMsg.ContainerName:
                response = await c2.on_container_start(inputMsg)
                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                    queue=mythic_container.CONTAINER_ON_START_RESPONSE,
                    body=response.to_json()
                )
                if response.RestartInternalServer:
                    t = asyncio.create_task(c2_utils.restartInternalServer(name=c2.name))
                return
        for name, pt in mythic_container.PayloadBuilder.payloadTypes.items():
            if pt.name == inputMsg.ContainerName:
                response = await pt.on_container_start(inputMsg)
                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                    queue=mythic_container.CONTAINER_ON_START_RESPONSE,
                    body=response.to_json()
                )
                return
        for name, tr in mythic_container.TranslationBase.translationServices.items():
            if tr.name == inputMsg.ContainerName:
                response = await tr.on_container_start(inputMsg)
                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                    queue=mythic_container.CONTAINER_ON_START_RESPONSE,
                    body=response.to_json()
                )
                return
        for name, lg in mythic_container.LoggingBase.loggers.items():
            if lg.name == inputMsg.ContainerName:
                response = await lg.on_container_start(inputMsg)
                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                    queue=mythic_container.CONTAINER_ON_START_RESPONSE,
                    body=response.to_json()
                )
                return
        for name, wb in mythic_container.WebhookBase.webhooks.items():
            if wb.name == inputMsg.ContainerName:
                response = await wb.on_container_start(inputMsg)
                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                    queue=mythic_container.CONTAINER_ON_START_RESPONSE,
                    body=response.to_json()
                )
                return
        for name, auth in mythic_container.AuthBase.authServices.items():
            if auth.name == inputMsg.ContainerName:
                response = await auth.on_container_start(inputMsg)
                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                    queue=mythic_container.CONTAINER_ON_START_RESPONSE,
                    body=response.to_json()
                )
                return
        for name, event in mythic_container.EventingBase.eventingServices.items():
            if event.name == inputMsg.ContainerName:
                response = await event.on_container_start(inputMsg)
                await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                    queue=mythic_container.CONTAINER_ON_START_RESPONSE,
                    body=response.to_json()
                )
                return
    except Exception as e:
        logger.exception(f"[-] Failed to call container on start with exception: {e}")
        return


async def consumingContainerReSync(msg: bytes) -> bytes:
    return ujson.dumps({"success": True}).encode()

payloadQueueTasks = []


async def startPayloadRabbitMQ(pt: PayloadBuilder.PayloadType) -> None:
    await startSharedServices(pt.name)
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(pt.name, mythic_container.PAYLOAD_BUILD_ROUTING_KEY),
        routing_key=getRoutingKey(pt.name, mythic_container.PAYLOAD_BUILD_ROUTING_KEY),
        handler=agent_utils.buildWrapper
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(pt.name, mythic_container.PT_ON_NEW_CALLBACK_ROUTING_KEY),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_ON_NEW_CALLBACK_ROUTING_KEY),
        handler=agent_utils.onNewCallback
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
        queue=getRoutingKey(pt.name, mythic_container.PT_RPC_COMMAND_TYPEDARRAY_PARSE_FUNCTION),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_RPC_COMMAND_TYPEDARRAY_PARSE_FUNCTION),
        handler=agent_utils.typedTaskParseFunction
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
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(pt.name, mythic_container.PT_CHECK_IF_CALLBACKS_ALIVE),
        routing_key=getRoutingKey(pt.name, mythic_container.PT_CHECK_IF_CALLBACKS_ALIVE),
        handler=agent_utils.checkIfCallbacksAlive
    )))


async def syncPayloadData(pt: PayloadBuilder.PayloadType) -> None:
    syncMessage = {
        "payload_type": pt.to_json(),
        "commands": [],
        "container_version": mythic_container.containerVersion
    }
    for cls in MythicCommandBase.CommandBase.__subclasses__():
        #if cls.__module__.split(".")[0].lower() == pt.name or pt.agent_code_path:
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
    await startSharedServices(c2.name)
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
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_REDIRECTOR_RULES_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_REDIRECTOR_RULES_ROUTING_KEY),
        handler=c2_utils.getRedirectorRules
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_OPSEC_CHECKS_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_OPSEC_CHECKS_ROUTING_KEY),
        handler=c2_utils.opsecChecks
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_STOP_SERVER_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_STOP_SERVER_ROUTING_KEY),
        handler=c2_utils.stopServer
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
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(c2.name, mythic_container.C2_RPC_HOST_FILE_ROUTING_KEY),
        routing_key=getRoutingKey(c2.name, mythic_container.C2_RPC_HOST_FILE_ROUTING_KEY),
        handler=c2_utils.hostFile
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
    await startSharedServices(tr.name)
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
    syncMessage = {
        "consuming_container": wb.get_sync_message(),
        "container_version": mythic_container.containerVersion
    }
    await startSharedServices(wb.name)
    while True:
        response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
            queue=mythic_container.CONSUMING_CONTAINER_SYNC_ROUTING_KEY,
            body=syncMessage)
        if response is None:
            logger.error("[-] Failed to get a response back from syncing RPC message, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif "success" not in response:
            logger.error("[-] RPC response doesn't contain success, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif not response["success"]:
            logger.error(f"[-] Failed to sync {wb.name}: {response['error']}, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        else:
            logger.info(f"[+] Successfully synced {wb.name}")
            break

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
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.CONSUMING_CONTAINER_RESYNC_ROUTING_KEY),
        routing_key=getRoutingKey(wb.name, mythic_container.CONSUMING_CONTAINER_RESYNC_ROUTING_KEY),
        handler=consumingContainerReSync
    )))
    logger.info(f"Successfully started webhook service")


async def syncLoggingData(wb: LoggingBase.Log) -> None:
    syncMessage = {
        "consuming_container": wb.get_sync_message(),
        "container_version": mythic_container.containerVersion
    }
    await startSharedServices(wb.name)
    while True:
        response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
            queue=mythic_container.CONSUMING_CONTAINER_SYNC_ROUTING_KEY,
            body=syncMessage)
        if response is None:
            logger.error("[-] Failed to get a response back from syncing RPC message, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif "success" not in response:
            logger.error("[-] RPC response doesn't contain success, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif not response["success"]:
            logger.error(f"[-] Failed to sync {wb.name}: {response['error']}, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        else:
            logger.info(f"[+] Successfully synced {wb.name}")
            break

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
    if wb.new_response is not None and callable(wb.new_response):
        payloadQueueTasks.append(
            asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectTopicExchange(
                queue=getLoggingRoutingKey(mythic_container.LOG_TYPE_RESPONSE),
                routing_key=getLoggingRoutingKey(mythic_container.LOG_TYPE_RESPONSE),
                handler=logging_utils.new_response
            )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.CONSUMING_CONTAINER_RESYNC_ROUTING_KEY),
        routing_key=getRoutingKey(wb.name, mythic_container.CONSUMING_CONTAINER_RESYNC_ROUTING_KEY),
        handler=consumingContainerReSync
    )))
    logger.info(f"Successfully started logging service")


async def syncAuthData(wb: AuthBase.Auth) -> None:
    syncMessage = {
        "consuming_container": wb.get_sync_message(),
        "container_version": mythic_container.containerVersion
    }
    await startSharedServices(wb.name)
    while True:
        response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
            queue=mythic_container.CONSUMING_CONTAINER_SYNC_ROUTING_KEY,
            body=syncMessage)
        if response is None:
            logger.error("[-] Failed to get a response back from syncing RPC message, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif "success" not in response:
            logger.error("[-] RPC response doesn't contain success, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif not response["success"]:
            logger.error(f"[-] Failed to sync {wb.name}: {response['error']}, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        else:
            logger.info(f"[+] Successfully synced {wb.name}")
            break

    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.AUTH_RPC_GET_IDP_METADATA),
        routing_key=getRoutingKey(wb.name, mythic_container.AUTH_RPC_GET_IDP_METADATA),
        handler=auth_utils.GetIDPMetadata
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.AUTH_RPC_GET_IDP_REDIRECT),
        routing_key=getRoutingKey(wb.name, mythic_container.AUTH_RPC_GET_IDP_REDIRECT),
        handler=auth_utils.GetIDPRedirect
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.AUTH_RPC_PROCESS_IDP_RESPONSE),
        routing_key=getRoutingKey(wb.name, mythic_container.AUTH_RPC_PROCESS_IDP_RESPONSE),
        handler=auth_utils.ProcessIDPResponse
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.AUTH_RPC_GET_NONIDP_METADATA),
        routing_key=getRoutingKey(wb.name, mythic_container.AUTH_RPC_GET_NONIDP_METADATA),
        handler=auth_utils.GetNonIDPMetadata
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.AUTH_RPC_GET_NONIDP_REDIRECT),
        routing_key=getRoutingKey(wb.name, mythic_container.AUTH_RPC_GET_NONIDP_REDIRECT),
        handler=auth_utils.GetNonIDPRedirect
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.AUTH_RPC_PROCESS_NONIDP_RESPONSE),
        routing_key=getRoutingKey(wb.name, mythic_container.AUTH_RPC_PROCESS_NONIDP_RESPONSE),
        handler=auth_utils.ProcessNonIDPResponse
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.CONSUMING_CONTAINER_RESYNC_ROUTING_KEY),
        routing_key=getRoutingKey(wb.name, mythic_container.CONSUMING_CONTAINER_RESYNC_ROUTING_KEY),
        handler=consumingContainerReSync
    )))
    logger.info(f"Successfully started auth service")


async def syncEventingData(wb: EventingBase.Eventing) -> None:
    syncMessage = {
        "consuming_container": wb.get_sync_message(),
        "container_version": mythic_container.containerVersion
    }
    await startSharedServices(wb.name)
    while True:
        response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(
            queue=mythic_container.CONSUMING_CONTAINER_SYNC_ROUTING_KEY,
            body=syncMessage)
        if response is None:
            logger.error("[-] Failed to get a response back from syncing RPC message, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif "success" not in response:
            logger.error("[-] RPC response doesn't contain success, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        elif not response["success"]:
            logger.error(f"[-] Failed to sync {wb.name}: {response['error']}, trying again...")
            await asyncio.sleep(failedConnectRetryDelay)
        else:
            logger.info(f"[+] Successfully synced {wb.name}")
            break

    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(wb.name, mythic_container.EVENTING_TASK_INTERCEPT),
        routing_key=getRoutingKey(wb.name, mythic_container.EVENTING_TASK_INTERCEPT),
        handler=eventing_utils.TaskIntercept
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(wb.name, mythic_container.EVENTING_RESPONSE_INTERCEPT),
        routing_key=getRoutingKey(wb.name, mythic_container.EVENTING_RESPONSE_INTERCEPT),
        handler=eventing_utils.ResponseIntercept
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(wb.name, mythic_container.EVENTING_CUSTOM_FUNCTION),
        routing_key=getRoutingKey(wb.name, mythic_container.EVENTING_CUSTOM_FUNCTION),
        handler=eventing_utils.CustomFunction
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(wb.name, mythic_container.EVENTING_CONDITIONAL_CHECK),
        routing_key=getRoutingKey(wb.name, mythic_container.EVENTING_CONDITIONAL_CHECK),
        handler=eventing_utils.ConditionalEventingCheck
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(wb.name, mythic_container.CONSUMING_CONTAINER_RESYNC_ROUTING_KEY),
        routing_key=getRoutingKey(wb.name, mythic_container.CONSUMING_CONTAINER_RESYNC_ROUTING_KEY),
        handler=consumingContainerReSync
    )))
    logger.info(f"Successfully started Eventing service")


async def startSharedServices(containerName: str):
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(containerName, mythic_container.CONTAINER_RPC_GET_FILE),
        routing_key=getRoutingKey(containerName, mythic_container.CONTAINER_RPC_GET_FILE),
        handler=getFile
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(containerName, mythic_container.CONTAINER_RPC_LIST_FILE),
        routing_key=getRoutingKey(containerName, mythic_container.CONTAINER_RPC_LIST_FILE),
        handler=listFile
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(containerName, mythic_container.CONTAINER_RPC_REMOVE_FILE),
        routing_key=getRoutingKey(containerName, mythic_container.CONTAINER_RPC_REMOVE_FILE),
        handler=removeFile
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromRPCQueue(
        queue=getRoutingKey(containerName, mythic_container.CONTAINER_RPC_WRITE_FILE),
        routing_key=getRoutingKey(containerName, mythic_container.CONTAINER_RPC_WRITE_FILE),
        handler=writeFile
    )))
    payloadQueueTasks.append(asyncio.create_task(mythic_container.RabbitmqConnection.ReceiveFromMythicDirectExchange(
        queue=getRoutingKey(containerName, mythic_container.CONTAINER_ON_START),
        routing_key=getRoutingKey(containerName, mythic_container.CONTAINER_ON_START),
        handler=onStart
    )))


async def start_services():
    initialize()
    logger.info(
        f"[+] Starting Services with version {mythic_container.containerVersion} and PyPi version {mythic_container.PyPi_version}\n")
    webhook_services = WebhookBase.Webhook.__subclasses__()
    for cls in webhook_services:
        logger.info(f"[*] Processing webhook service")
        webhook = cls()
        if webhook.name == "":
            logger.error("missing name for webhook")
            continue
        if webhook.name in WebhookBase.webhooks:
            logger.error(f"[-] attempting to import {webhook.name} multiple times - probably due to import issues")
            continue
        WebhookBase.webhooks[webhook.name] = webhook
        await syncWebhookData(webhook)
    logging_services = LoggingBase.Log.__subclasses__()
    for cls in logging_services:
        logger.info(f"[*] Processing logging services")
        definedLog = cls()
        if definedLog.name == "":
            logger.error("missing name for logger")
            continue
        if definedLog.name in LoggingBase.loggers:
            logger.error(f"[-] attempting to import {definedLog.name} multiple times - probably due to import issues")
            continue
        LoggingBase.loggers[definedLog.name] = definedLog
        await syncLoggingData(definedLog)
    payloadTypes = PayloadBuilder.PayloadType.__subclasses__()
    for cls in payloadTypes:
        payload_type = cls()
        if payload_type.name == "":
            logger.error("missing name for payload_type")
            continue
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
        if c2profile.name == "":
            logger.error("missing name for c2profile")
            continue
        if c2profile.name in C2ProfileBase.c2Profiles:
            logger.error(f"[-] attempting to import {c2profile.name} multiple times - probably due to import issues")
            continue
        C2ProfileBase.c2Profiles[c2profile.name] = c2profile
        logger.info(f"[*] Processing c2 profile: {c2profile.name}")
        await syncC2ProfileData(c2profile)
        await startC2RabbitMQ(c2profile)

    translation_services = TranslationBase.TranslationContainer.__subclasses__()
    for cls in translation_services:
        translator = cls()
        if translator.name == "":
            logger.error("missing name for translator")
            continue
        if translator.name in TranslationBase.translationServices:
            logger.error(f"[-] attempting to import {translator.name} multiple times - probably due to import issues")
            continue
        TranslationBase.translationServices[translator.name] = translator
        logger.info(f"[*] Processing translation service: {translator.name}")
        await syncTranslatorData(translator)
        await startTranslatorRabbitMQ(translator)
    auth_services = AuthBase.Auth.__subclasses__()
    for cls in auth_services:
        auth = cls()
        if auth.name == "":
            logger.error("missing name for auth service")
            continue
        if auth.name in AuthBase.authServices:
            logger.error(f"[-] attempting to import {auth.name} multiple times - probably due to import issues")
            continue
        AuthBase.authServices[auth.name] = auth
        logger.info(f"[*] Processing auth service: {auth.name}")
        await syncAuthData(auth)
    eventing_services = EventingBase.Eventing.__subclasses__()
    for cls in eventing_services:
        event = cls()
        if event.name == "":
            logger.error("missing name for event service")
            continue
        if event.name in EventingBase.eventingServices:
            logger.error(f"[-] attempting to import {event.name} multiple times - probably due to import issues")
            continue
        EventingBase.eventingServices[event.name] = event
        logger.info(f"[*] Processing eventing service: {event.name}")
        await syncEventingData(event)

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
            for cmdcls in MythicCommandBase.CommandBase.__subclasses__():
                if cmdcls.__module__.split(".")[0] == payload_type.name:
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
