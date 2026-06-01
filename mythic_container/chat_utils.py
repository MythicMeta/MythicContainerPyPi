import traceback

import ujson

import mythic_container
from . import ChatBase
from .logging import logger


async def ChatRequestHandler(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        request = ChatBase.ChatRequest(**msgDict)
        for name, chat in ChatBase.chatServices.items():
            if chat.name == request.ContainerName:
                if chat.chat is None:
                    await ChatBase.SendMythicRPCChatResponse(ChatBase.ChatResponse(
                        OperationID=request.OperationID,
                        RequestID=request.RequestID,
                        ResponseMessageID=request.ResponseMessageID,
                        Status="error",
                        Error=f"{chat.name} does not implement a chat function",
                    ))
                    return
                await chat.chat(request)
                return
        await ChatBase.SendMythicRPCChatResponse(ChatBase.ChatResponse(
            OperationID=request.OperationID,
            RequestID=request.RequestID,
            ResponseMessageID=request.ResponseMessageID,
            Status="error",
            Error=f"Failed to find chat service {request.ContainerName}",
        ))
    except Exception as e:
        logger.exception(f"[-] Failed to process chat request: {e}")
        try:
            msgDict = ujson.loads(msg)
            await ChatBase.SendMythicRPCChatResponse(ChatBase.ChatResponse(
                OperationID=msgDict.get("operation_id", 0),
                RequestID=msgDict.get("request_id", 0),
                ResponseMessageID=msgDict.get("response_message_id", 0),
                Status="error",
                Error=f"Hit exception trying to process chat request: {traceback.format_exc()}",
            ))
        except Exception:
            logger.exception("[-] Failed to send chat request error response")
