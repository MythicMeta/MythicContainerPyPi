import aiohttp

from .MythicGoRPC import SendMythicRPCDirectFileTokenCreate, MythicRPCDirectFileTokenCreateMessage
from .config import settings
from .logging import logger


async def sendFileToMythic(contents: bytes, agentFileId: str) -> bool:
    try:
        tokenResponse = await SendMythicRPCDirectFileTokenCreate(MythicRPCDirectFileTokenCreateMessage(
            AgentFileID=agentFileId,
            Action="upload",
        ))
        if not tokenResponse.Success:
            logger.info(f"[!] Failed to get file upload token: {tokenResponse.Error}")
            return False
        async with aiohttp.ClientSession(headers={
            "Authorization": f"Bearer {tokenResponse.Token}"
        }) as session:
            data = aiohttp.FormData()
            url = f"http://{settings.get('mythic_server_host')}:{settings.get('mythic_server_port', 17443)}/direct/upload/{agentFileId}"
            data.add_field('file', contents, filename='payload', )
            async with session.post(url, data=data, ssl=False) as resp:
                if resp.status == 200:
                    responseData = await resp.json()
                    if "status" in responseData and responseData["status"] == "success":
                        logger.info(f"[+] Successfully uploaded file contents to Mythic")
                        return True
                    else:
                        logger.error(f"[-] Failed to upload file contents to Mythic")
                        return False
                else:
                    logger.error(f"[-] Failed to upload file contents to Mythic")
                    return False
    except Exception as e:
        logger.exception(f"[-] Failed to upload payload contents: {e}")
        return False


async def getFileFromMythic(agentFileId: str) -> bytes:
    try:
        tokenResponse = await SendMythicRPCDirectFileTokenCreate(MythicRPCDirectFileTokenCreateMessage(
            AgentFileID=agentFileId,
            Action="download",
        ))
        if not tokenResponse.Success:
            logger.info(f"[!] Failed to get file download token: {tokenResponse.Error}")
            raise Exception("[!] Failed to get file download token")
        async with aiohttp.ClientSession(headers={
            "Authorization": f"Bearer {tokenResponse.Token}"
        }) as session:
            url = f"http://{settings.get('mythic_server_host')}:{settings.get('mythic_server_port', 17443)}/direct/download/{agentFileId}"
            async with session.get(url, ssl=False) as resp:
                if resp.status == 200:
                    responseData = await resp.read()
                    return responseData
                else:
                    logger.error(f"[-] Failed to download file from Mythic: {resp.status}")
                    raise Exception("[-] Failed to download file from Mythic")
    except Exception as e:
        logger.exception(f"[-] Failed to get file contents: {e}")
        raise Exception("[-] Failed to download file from Mythic")