import asyncio
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
                        ResponseKey="system:not-implemented",
                        Complete=True,
                        CompleteRequest=True,
                        Status="error",
                        Error=f"{chat.name} does not implement a chat function",
                    ))
                    return
                if request.RequestID > 0 and request.RequestID in ChatBase.chatCancelledRequests:
                    ChatBase.chatCancelledRequests.discard(request.RequestID)
                    await ChatBase.SendMythicRPCChatResponse(ChatBase.ChatResponse(
                        OperationID=request.OperationID,
                        RequestID=request.RequestID,
                        ResponseKey="system:cancelled",
                        Complete=True,
                        CompleteRequest=True,
                        Status="cancelled",
                        Error="Cancelled by operator",
                    ))
                    return
                task = asyncio.create_task(chat.chat(request))
                if request.RequestID > 0:
                    ChatBase.chatRequestTasks[request.RequestID] = task
                try:
                    await task
                except asyncio.CancelledError:
                    await ChatBase.SendMythicRPCChatResponse(ChatBase.ChatResponse(
                        OperationID=request.OperationID,
                        RequestID=request.RequestID,
                        ResponseKey="system:cancelled",
                        Complete=True,
                        CompleteRequest=True,
                        Status="cancelled",
                        Error="Cancelled by operator",
                    ))
                finally:
                    if request.RequestID > 0 and ChatBase.chatRequestTasks.get(request.RequestID) is task:
                        ChatBase.chatRequestTasks.pop(request.RequestID, None)
                return
        await ChatBase.SendMythicRPCChatResponse(ChatBase.ChatResponse(
            OperationID=request.OperationID,
            RequestID=request.RequestID,
            ResponseKey="system:not-found",
            Complete=True,
            CompleteRequest=True,
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
                ResponseKey="system:exception",
                Complete=True,
                CompleteRequest=True,
                Status="error",
                Error=f"Hit exception trying to process chat request: {traceback.format_exc()}",
            ))
        except Exception:
            logger.exception("[-] Failed to send chat request error response")


async def ChatCancelHandler(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        request = ChatBase.ChatCancelRequest(**msgDict)
        task = ChatBase.chatRequestTasks.get(request.RequestID)
        if task is not None and not task.done():
            task.cancel()
        elif request.RequestID > 0:
            ChatBase.chatCancelledRequests.add(request.RequestID)
    except Exception as e:
        logger.exception(f"[-] Failed to process chat cancellation: {e}")
