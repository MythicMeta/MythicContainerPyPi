from .logging import logger
import ujson
import mythic_container.C2ProfileBase
import psutil
import os
import subprocess
import asyncio
import traceback


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


async def deal_with_stdout(c2_profile: str) -> str:
    output = ""
    lines = 0
    while True:
        try:
            line = await asyncio.wait_for(
                mythic_container.C2ProfileBase.runningServers[c2_profile]["process"].stdout.readline(), timeout=3.0)
            output += line.decode()
            lines += 1
            if lines > 100:
                break
        except asyncio.TimeoutError:
            break
        except Exception as e:
            logger.exception(f"hit exception trying to get server output: {traceback.format_exc()}")
            return output + traceback.format_exc()
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
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2OPSECMessageResponse):
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
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2ConfigCheckMessageResponse):
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
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2GetIOCMessageResponse):
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
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2SampleMessageMessageResponse):
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


async def getFile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                response = mythic_container.C2ProfileBase.C2GetFileMessageResponse(Success=False)
                try:
                    inputMsg = mythic_container.C2ProfileBase.C2GetFileMessage(**msgDict)
                    path = c2.server_folder_path / inputMsg.Filename
                    path = path.resolve()
                    if c2.server_folder_path.resolve() not in path.parents:
                        response.Success = False
                        response.Error = "Attempt to access outside of the c2 server folder"
                    else:
                        file_data = open(path, "rb").read()
                        response.Success = True
                        response.Message = file_data
                except Exception as e:
                    response.Error = f"{traceback.format_exc()}\n{e}"
                return ujson.dumps(response.to_json()).encode()
        response = mythic_container.C2ProfileBase.C2GetFileMessageResponse(
            Success=False, Error="Failed to find that c2 profile",
        )
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2GetFileMessageResponse(
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
                        return ujson.dumps(response).encode()
                    elif isinstance(result, mythic_container.C2ProfileBase.C2GetRedirectorRulesMessageResponse):
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


async def listFile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                response = mythic_container.C2ProfileBase.C2ListFileMessageResponse(Success=False)
                try:
                    path = c2.server_folder_path
                    files = os.listdir(path)
                    files = [f for f in files if os.path.isfile(path / f)]
                    response.Files = files
                    response.Success = True
                except Exception as e:
                    response.Error = f"{traceback.format_exc()}\n{e}"
                return ujson.dumps(response.to_json()).encode()
        response = mythic_container.C2ProfileBase.C2ListFileMessageResponse(
            Success=False, Error="Failed to find that c2 profile",
        )
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2ListFileMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call list file function function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def removeFile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                response = mythic_container.C2ProfileBase.C2RemoveFileMessageResponse(Success=False)
                try:
                    inputMsg = mythic_container.C2ProfileBase.C2RemoveFileMessage(**msgDict)
                    path = c2.server_folder_path / inputMsg.Filename
                    path = path.resolve()
                    if c2.server_folder_path.resolve() not in path.parents:
                        response.Success = False
                        response.Error = "Attempt to access outside of the c2 server folder"
                    else:
                        os.remove(path)
                        response.Success = True
                except Exception as e:
                    response.Error = f"{traceback.format_exc()}\n{e}"
                return ujson.dumps(response.to_json()).encode()
        response = mythic_container.C2ProfileBase.C2GetFileMessageResponse(
            Success=False, Error="Failed to find that c2 profile",
        )
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = mythic_container.C2ProfileBase.C2GetFileMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get debug output function function: {traceback.format_exc()}\n{e}"
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
                        mythic_container.C2ProfileBase.runningServers[c2.name]["output"] = ""
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


async def writeFile(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, c2 in mythic_container.C2ProfileBase.c2Profiles.items():
            if c2.name == msgDict["c2_profile_name"]:
                response = mythic_container.C2ProfileBase.C2WriteFileMessageResponse(Success=False)
                try:
                    inputMsg = mythic_container.C2ProfileBase.C2WriteFileMessage(**msgDict)
                    path = c2.server_folder_path / inputMsg.Filename
                    path = path.resolve()
                    if c2.server_folder_path.resolve() not in path.parents:
                        response.Success = False
                        response.Error = "Attempt to write outside of the c2 server folder"
                    else:
                        with open(path, "wb") as f:
                            f.write(inputMsg.Contents)
                        response.Success = True
                        response.Message = "Successfully wrote file"
                except Exception as e:
                    logger.exception(f"[-] Failed to write to file: {e}")
                    response.Error = f"{traceback.format_exc()}\n{e}"
                return ujson.dumps(response.to_json()).encode()
        response = mythic_container.C2ProfileBase.C2WriteFileMessageResponse(
            Success=False, Error="Failed to find that c2 profile",
        )
        return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        logger.exception(f"[-] Failed to write to file with exception: {e}")
        response = mythic_container.C2ProfileBase.C2WriteFileMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call write file function function: {traceback.format_exc()}\n{e}"
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
