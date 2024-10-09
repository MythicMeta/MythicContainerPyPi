from .logging import logger
import ujson
import mythic_container.C2ProfileBase
import psutil
import os
import subprocess
import asyncio
import traceback
from collections import deque
from threading import Lock
from mythic_container.MythicGoRPC.send_mythic_rpc_c2_update_status import *

c2Mutex = Lock()


def kill(proc_pid):
    try:
        target_processes = psutil.Process(proc_pid)
        for proc in target_processes.children(recursive=True):
            proc.kill()
        target_processes.kill()
    except psutil.NoSuchProcess:
        pass
    except Exception as e:
        logger.exception(f"[-] Failed to kill process: {e}")


async def keep_reading_stdout(c2_profile: str):
    if "reading" in mythic_container.C2ProfileBase.runningServers[c2_profile]:
        return
    while True:
        mythic_container.C2ProfileBase.runningServers[c2_profile]["reading"] = 1
        try:
            line = await asyncio.wait_for(
                mythic_container.C2ProfileBase.runningServers[c2_profile]["process"].stdout.readline(), timeout=3.0)
            if line is not None:
                if len(line) == 0:
                    # the process has stopped, but our loop will keep returning blank lines
                    if mythic_container.C2ProfileBase.runningServers[c2_profile]["process"].returncode is not None:
                        del mythic_container.C2ProfileBase.runningServers[c2_profile]["reading"]
                        return
                    continue
                logger.debug(line.decode())
                if "output" in mythic_container.C2ProfileBase.runningServers[c2_profile]:
                    mythic_container.C2ProfileBase.runningServers[c2_profile]["output"].append(line.decode())
                else:
                    mythic_container.C2ProfileBase.runningServers[c2_profile]["output"] = deque([line.decode()], 100)
        except TimeoutError:
            await asyncio.sleep(1)
            continue
        except Exception as e:
            logger.exception(f"hit exception trying to get server output: {traceback.format_exc()}")
            del mythic_container.C2ProfileBase.runningServers[c2_profile]["reading"]
            return


async def deal_with_stdout(c2_profile: str) -> str:
    output = ""
    if "output" in mythic_container.C2ProfileBase.runningServers[c2_profile]:
        try:
            while True:
                output += mythic_container.C2ProfileBase.runningServers[c2_profile]["output"].popleft()
        except IndexError:
            pass
        except Exception as e:
            logger.exception(f"hit exception trying to read server output: {traceback.format_exc()}")
    return output


async def opsecChecks(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                if callable(c2.opsec):
                    try:
                        result = await c2.opsec(mythic_container.C2ProfileBase.C2OPSECMessage(**msgDict))
                    except Exception as callEx:
                        logger.exception(
                            f"Failed to call opsec for {c2.name}")
                        response = mythic_container.C2ProfileBase.C2OPSECMessageResponse(
                            Success=False,
                            Error=f"Failed to call opsec function: {traceback.format_exc()}\n{callEx}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    if result is None:
                        response = mythic_container.C2ProfileBase.C2OPSECMessageResponse(
                            Success=False,
                            Error=f"Failed to call opsec function: No result returned"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    elif isinstance(result, dict):
                        response = mythic_container.C2ProfileBase.C2OPSECMessageResponse(**result)
                        if response.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2OPSECMessageResponse):
                        if result.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(result.to_json()).encode()
                    else:
                        response = mythic_container.C2ProfileBase.C2OPSECMessageResponse(
                            Success=False,
                            Error=f"unknown result type from function: {result}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                else:
                    logger.error(f"opsec function for {c2.name} isn't callable")
                    response = mythic_container.C2ProfileBase.C2OPSECMessageResponse(
                        Success=False,
                        Error=f"opsec function for {c2.name} isn't callable"
                    )
                    return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2OPSECMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call opsec function function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def configChecks(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                if callable(c2.opsec):
                    try:
                        result = await c2.config_check(mythic_container.C2ProfileBase.C2ConfigCheckMessage(**msgDict))
                    except Exception as callEx:
                        logger.exception(
                            f"Failed to call config check for {c2.name}")
                        response = mythic_container.C2ProfileBase.C2ConfigCheckMessageResponse(
                            Success=False,
                            Error=f"Failed to call config check function: {traceback.format_exc()}\n{callEx}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    if result is None:
                        response = mythic_container.C2ProfileBase.C2ConfigCheckMessageResponse(
                            Success=False,
                            Error=f"Failed to call config check function: No result returned"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    elif isinstance(result, dict):
                        response = mythic_container.C2ProfileBase.C2ConfigCheckMessageResponse(**result)
                        if response.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2ConfigCheckMessageResponse):
                        if result.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(result.to_json()).encode()
                    else:
                        response = mythic_container.C2ProfileBase.C2ConfigCheckMessageResponse(
                            Success=False,
                            Error=f"unknown result type from function: {result}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                else:
                    logger.error(f"config check function for {c2.name} isn't callable")
                    response = mythic_container.C2ProfileBase.C2ConfigCheckMessageResponse(
                        Success=False,
                        Error=f"config check function for {c2.name} isn't callable"
                    )
                    return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2ConfigCheckMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call config check function function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def getIOC(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                if callable(c2.get_ioc):
                    try:
                        result = await c2.config_check(mythic_container.C2ProfileBase.C2GetIOCMessage(**msgDict))
                    except Exception as callEx:
                        logger.exception(
                            f"Failed to call get_ioc for {c2.name}")
                        response = mythic_container.C2ProfileBase.C2GetIOCMessageResponse(
                            Success=False,
                            Error=f"Failed to call config check function: {traceback.format_exc()}\n{callEx}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    if result is None:
                        response = mythic_container.C2ProfileBase.C2GetIOCMessageResponse(
                            Success=False,
                            Error=f"Failed to call config check function: No result returned"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    elif isinstance(result, dict):
                        response = mythic_container.C2ProfileBase.C2GetIOCMessageResponse(**result)
                        if response.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2GetIOCMessageResponse):
                        if result.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(result.to_json()).encode()
                    else:
                        response = mythic_container.C2ProfileBase.C2GetIOCMessageResponse(
                            Success=False,
                            Error=f"unknown result type from function: {result}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                else:
                    logger.error(f"get_ioc function for {c2.name} isn't callable")
                    response = mythic_container.C2ProfileBase.C2GetIOCMessageResponse(
                        Success=False,
                        Error=f"get ioc function for {c2.name} isn't callable"
                    )
                    return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2GetIOCMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get_ioc function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def sampleMessage(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                if callable(c2.sample_message):
                    try:
                        result = await c2.config_check(mythic_container.C2ProfileBase.C2SampleMessageMessage(**msgDict))
                    except Exception as callEx:
                        logger.exception(
                            f"Failed to call get_ioc for {c2.name}")
                        response = mythic_container.C2ProfileBase.C2SampleMessageMessageResponse(
                            Success=False,
                            Error=f"Failed to call sample_message function: {traceback.format_exc()}\n{callEx}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    if result is None:
                        response = mythic_container.C2ProfileBase.C2SampleMessageMessageResponse(
                            Success=False,
                            Error=f"Failed to call sample message function: No result returned"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    elif isinstance(result, dict):
                        response = mythic_container.C2ProfileBase.C2SampleMessageMessageResponse(**result)
                        if response.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2SampleMessageMessageResponse):
                        if result.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(result.to_json()).encode()
                    else:
                        response = mythic_container.C2ProfileBase.C2SampleMessageMessageResponse(
                            Success=False,
                            Error=f"unknown result type from function: {result}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                else:
                    logger.error(f"sample_message function for {c2.name} isn't callable")
                    response = mythic_container.C2ProfileBase.C2SampleMessageMessageResponse(
                        Success=False,
                        Error=f"sample message function for {c2.name} isn't callable"
                    )
                    return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2SampleMessageMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call sample_message function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def getDebugOutput(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                if mythic_container.C2ProfileBase.runningServers[c2.name]["process"] is not None:
                    if mythic_container.C2ProfileBase.runningServers[c2.name]["process"].returncode is None:
                        running = True
                    else:
                        running = False
                        try:
                            kill(mythic_container.C2ProfileBase.runningServers[c2.name]["process"].pid)
                        except Exception as e:
                            pass
                    response = mythic_container.C2ProfileBase.C2GetDebugOutputMessageResponse(
                        Success=True, Error="", Message=f"{await deal_with_stdout(c2.name)}",
                        InternalServerRunning=running
                    )
                    return ujson.dumps(response.to_json()).encode()
                else:
                    response = mythic_container.C2ProfileBase.C2GetDebugOutputMessageResponse(
                        Success=True, Error="", Message="Server not running",
                        InternalServerRunning=False
                    )
                    return ujson.dumps(response.to_json()).encode()
        response = mythic_container.C2ProfileBase.C2GetDebugOutputMessageResponse(
            Success=False, Error="Failed to find that c2 profile",
            InternalServerRunning=False
        )
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2GetDebugOutputMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get debug output function function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def getRedirectorRules(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                if callable(c2.redirect_rules):
                    try:
                        result = await c2.redirect_rules(
                            mythic_container.C2ProfileBase.C2GetRedirectorRulesMessage(**msgDict))
                    except Exception as callEx:
                        logger.exception(
                            f"Failed to call get redirector rules for {c2.name}")
                        response = mythic_container.C2ProfileBase.C2GetRedirectorRulesMessageResponse(
                            Success=False,
                            Error=f"Failed to call get redirector rules function: {traceback.format_exc()}\n{callEx}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    if result is None:
                        response = mythic_container.C2ProfileBase.C2GetRedirectorRulesMessageResponse(
                            Success=False,
                            Error=f"Failed to call get redirector rules function: No result returned"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    elif isinstance(result, dict):
                        response = mythic_container.C2ProfileBase.C2GetRedirectorRulesMessageResponse(**result)
                        if response.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2GetRedirectorRulesMessageResponse):
                        if result.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(result.to_json()).encode()
                    else:
                        response = mythic_container.C2ProfileBase.C2GetRedirectorRulesMessageResponse(
                            Success=False,
                            Error=f"unknown result type from function: {result}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                else:
                    logger.error(f"get redirector rules function for {c2.name} isn't callable")
                    response = mythic_container.C2ProfileBase.C2GetRedirectorRulesMessageResponse(
                        Success=False,
                        Error=f"get redirector rules function for {c2.name} isn't callable"
                    )
                    return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2GetRedirectorRulesMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get redirector rules function function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def startServerBinary(
        c2: mythic_container.C2ProfileBase.C2Profile) -> mythic_container.C2ProfileBase.C2StartServerMessageResponse:
    try:
        if c2.name not in mythic_container.C2ProfileBase.runningServers:
            mythic_container.C2ProfileBase.runningServers[c2.name] = {
                "process": None
            }
        path = c2.server_binary_path.resolve()
        cwd = c2.server_folder_path.resolve()
        os.chmod(path, mode=0o777)
        process = await asyncio.create_subprocess_shell(cmd=str(path), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                        shell=True, cwd=str(cwd), env=os.environ.copy())
        mythic_container.C2ProfileBase.runningServers[c2.name]["process"] = process
        asyncio.create_task(keep_reading_stdout(c2.name))
        await asyncio.sleep(3)
        if process.returncode is not None:
            # this means something went wrong and the process is dead
            return mythic_container.C2ProfileBase.C2StartServerMessageResponse(
                Success=False,
                Error=f"Failed to start\nOutput:\n{await deal_with_stdout(c2.name)}",
                InternalServerRunning=False
            )
        else:
            return mythic_container.C2ProfileBase.C2StartServerMessageResponse(
                Success=True,
                Message=f"Started with pid: {process.pid}...\nOutput:{await deal_with_stdout(c2.name)}",
                InternalServerRunning=True
            )
    except Exception as e:
        return mythic_container.C2ProfileBase.C2StartServerMessageResponse(
            Success=False,
            Error=f"Failed to start server: {traceback.format_exc()}\n{e}",
            Message=f"Failed to start server: {traceback.format_exc()}\n{e}",
            InternalServerRunning=False
        )


async def startServer(msg: bytes) -> bytes:
    with c2Mutex:
        try:
            msgDict = ujson.loads(msg)
            for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
                if c2.name == msgDict["c2_profile_name"]:
                    if c2.name in mythic_container.C2ProfileBase.runningServers:
                        # we've at least started this before, so we can check some keys
                        if mythic_container.C2ProfileBase.runningServers[c2.name]["process"] is None:
                            # process isn't running, so we need to start it
                            response = await startServerBinary(c2)
                            return ujson.dumps(response.to_json()).encode()

                        elif mythic_container.C2ProfileBase.runningServers[c2.name]["process"].returncode is None:
                            response = mythic_container.C2ProfileBase.C2StartServerMessageResponse(
                                Success=True, Error="", Message=await deal_with_stdout(c2.name),
                                InternalServerRunning=True
                            )
                            return ujson.dumps(response.to_json()).encode()
                        else:
                            try:
                                kill(mythic_container.C2ProfileBase.runningServers[c2.name]["process"].pid)
                            except Exception as e:
                                pass
                            # now try to start it again
                            response = await startServerBinary(c2)
                            return ujson.dumps(response.to_json()).encode()
                    else:
                        # just means we've never started it before, so start it now
                        response = await startServerBinary(c2)
                        return ujson.dumps(response.to_json()).encode()
            response = mythic_container.C2ProfileBase.C2StartServerMessageResponse(
                Success=False, Error="Failed to find that c2 profile",
                InternalServerRunning=False
            )
            return ujson.dumps(response.to_json()).encode()
        except Exception as e:
            response = mythic_container.C2ProfileBase.C2StartServerMessageResponse(
                Success=False,
                Error=f"Hit exception trying to call server start function function: {traceback.format_exc()}\n{e}"
            )
            return ujson.dumps(response.to_json()).encode()


async def stopServer(msg: bytes) -> bytes:
    with c2Mutex:
        try:
            msgDict = ujson.loads(msg)
            for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
                if c2.name == msgDict["c2_profile_name"]:
                    if c2.name in mythic_container.C2ProfileBase.runningServers:
                        # we've at least started this before, so we can check some keys
                        if mythic_container.C2ProfileBase.runningServers[c2.name]["process"] is None:
                            # process isn't running, so we need to start it
                            response = mythic_container.C2ProfileBase.C2StopServerMessageResponse(
                                Success=True, Error="", Message=f"The server is not running",
                                InternalServerRunning=False
                            )
                            return ujson.dumps(response.to_json()).encode()

                        elif mythic_container.C2ProfileBase.runningServers[c2.name]["process"].returncode is not None:
                            # the process was running, but died at some point before we tried to stop it
                            response = mythic_container.C2ProfileBase.C2StartServerMessageResponse(
                                Success=True, Error="", Message=f"{await deal_with_stdout(c2.name)}",
                                InternalServerRunning=False
                            )
                            return ujson.dumps(response.to_json()).encode()
                        else:
                            try:
                                kill(mythic_container.C2ProfileBase.runningServers[c2.name]["process"].pid)
                            except Exception as e:
                                pass
                            # now try to start it again
                            await asyncio.sleep(3)
                            response = mythic_container.C2ProfileBase.C2StopServerMessageResponse(
                                Success=True, Error="",
                                Message=f"Stopped server:\nOutput:{await deal_with_stdout(c2.name)}",
                                InternalServerRunning=False
                            )
                            if "output" in mythic_container.C2ProfileBase.runningServers[c2.name]:
                                mythic_container.C2ProfileBase.runningServers[c2.name]["output"].clear()
                            return ujson.dumps(response.to_json()).encode()
                    else:
                        # just means we've never started it before, so start it now
                        response = mythic_container.C2ProfileBase.C2StopServerMessageResponse(
                            Success=True, Error="", Message=f"The server was never started",
                            InternalServerRunning=False
                        )
                        return ujson.dumps(response.to_json()).encode()
            response = mythic_container.C2ProfileBase.C2StartServerMessageResponse(
                Success=False, Error="Failed to find that c2 profile",
                InternalServerRunning=False
            )
            return ujson.dumps(response.to_json()).encode()
        except Exception as e:
            response = mythic_container.C2ProfileBase.C2StartServerMessageResponse(
                Success=False,
                Error=f"Hit exception trying to call server start function function: {traceback.format_exc()}\n{e}"
            )
            return ujson.dumps(response.to_json()).encode()


async def customRPCFunction(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        incomingMessage = mythic_container.C2ProfileBase.C2OtherServiceRPCMessage(**msgDict)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == incomingMessage.ServiceName:
                if c2.custom_rpc_functions is not None:
                    for key, f in c2.custom_rpc_functions.items():
                        if key == incomingMessage.ServiceRPCFunction:
                            response = await f(incomingMessage)
                            if response.RestartInternalServer:
                                t = asyncio.create_task(restartInternalServer(name=c2.name))
                            return ujson.dumps(response.to_json()).encode()
                    response = mythic_container.C2ProfileBase.C2OtherServiceRPCMessageResponse(
                        Success=False,
                        Error=f"Failed to find function {incomingMessage.ServiceRPCFunction} in custom rpc functions for {c2.name}"
                    )
                    return ujson.dumps(response.to_json()).encode()
                else:
                    response = mythic_container.C2ProfileBase.C2OtherServiceRPCMessageResponse(
                        Success=False,
                        Error=f"No custom rpc functions defined for payload {c2.name}"
                    )
                    return ujson.dumps(response.to_json()).encode()
        response = mythic_container.C2ProfileBase.C2OtherServiceRPCMessageResponse(
            Success=False,
            Error=f"Failed to find service: {incomingMessage.ServiceName}"
        )
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2OtherServiceRPCMessageResponse(
            Success=False,
            Error=f"Failed to call custom RPC function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def reSyncC2Profile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                await mythic_container.mythic_service.syncC2ProfileData(c2)
                return ujson.dumps({"success": True}).encode()
        return ujson.dumps({"success": False, "error": "Failed to find c2 profile"}).encode()
    except Exception as e:
        logger.exception(f"Failed to re-sync c2 profile: {e}")
        return ujson.dumps({"success": False, "error": f"Failed to sync: {traceback.format_exc()}\n{e}"}).encode()


async def hostFile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                if callable(c2.host_file):
                    try:
                        result = await c2.host_file(mythic_container.C2ProfileBase.C2HostFileMessage(**msgDict))
                    except Exception as callEx:
                        logger.exception(
                            f"Failed to call host_file for {c2.name}")
                        response = mythic_container.C2ProfileBase.C2HostFileMessageResponse(
                            Success=False,
                            Error=f"Failed to call config check function: {traceback.format_exc()}\n{callEx}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    if result is None:
                        response = mythic_container.C2ProfileBase.C2HostFileMessageResponse(
                            Success=False,
                            Error=f"Failed to call host file: No result returned"
                        )
                        return ujson.dumps(response.to_json()).encode()
                    elif isinstance(result, dict):
                        response = mythic_container.C2ProfileBase.C2HostFileMessageResponse(**result)
                        if response.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2HostFileMessageResponse):
                        if result.RestartInternalServer:
                            t = asyncio.create_task(restartInternalServer(name=c2.name))
                        return ujson.dumps(result.to_json()).encode()
                    else:
                        response = mythic_container.C2ProfileBase.C2HostFileMessageResponse(
                            Success=False,
                            Error=f"unknown result type from function: {result}"
                        )
                        return ujson.dumps(response.to_json()).encode()
                else:
                    logger.error(f"host_file function for {c2.name} isn't callable")
                    response = mythic_container.C2ProfileBase.C2HostFileMessageResponse(
                        Success=False,
                        Error=f"host file function for {c2.name} isn't callable"
                    )
                    return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2HostFileMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call host_file function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def restartInternalServer(name: str):
    stop_response = await stopServer(ujson.dumps({"c2_profile_name": name}).encode())
    start_response = await startServer(ujson.dumps({"c2_profile_name": name}).encode())
    startResponse = ujson.loads(start_response)
    await SendMythicRPCC2UpdateStatus(MythicRPCC2UpdateStatusMessage(
        C2Profile=name,
        InternalServerRunning=startResponse["server_running"] if "server_running" in startResponse else False,
        Error=startResponse["error"] if "error" in startResponse else "",
    ))