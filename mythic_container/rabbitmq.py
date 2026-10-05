import concurrent.futures

import aiormq.exceptions

from .logging import logger
import aio_pika
import base64
import mythic_container
from .config import settings
from collections.abc import Callable, Awaitable
from typing import Coroutine, Optional
import ujson
import asyncio
from functools import partial
import uuid
import hashlib
import hmac
import secrets
import time
import contextvars
from typing import MutableMapping


mutex = asyncio.Lock()

failedConnectRetryDelay = 5
failedConnectTimeout = 1

MYTHIC_AUTH_CONTEXT_HEADER = "mythic-auth-context"
MYTHIC_CONTAINER_PRINCIPAL_HEADER = "mythic-container-principal"
MYTHIC_CONTAINER_TIMESTAMP_HEADER = "mythic-container-timestamp"
MYTHIC_CONTAINER_NONCE_HEADER = "mythic-container-nonce"
MYTHIC_CONTAINER_SIGNATURE_HEADER = "mythic-container-signature"
_request_auth_contexts: dict[str, tuple[str, float, bool]] = {}
_current_auth_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "mythic_rabbitmq_auth_context", default=None
)
AUTH_CONTEXT_CACHE_TTL = 24 * 60 * 60
AUTH_CONTEXT_CACHE_LIMIT = 16384
MYTHIC_RPC_REPLY_EXCHANGE = "mythic_rpc_reply_exchange"


def _auth_context_keys(value, parent: str = "", depth: int = 0) -> set[str]:
    if depth > 6:
        return set()
    result: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = f"{parent}_id" if key == "id" and parent in {"task", "callback"} else key
            if normalized_key in {
                "operation_id", "task_id", "callback_id", "agent_callback_id",
                "eventstepinstance_id", "uuid", "payload_uuid", "build_uuid",
            }:
                if isinstance(child, int) and child > 0:
                    result.add(f"{normalized_key}:{child}")
                elif isinstance(child, str) and child:
                    result.add(f"{normalized_key}:{child}")
            result.update(_auth_context_keys(child, key, depth + 1))
    elif isinstance(value, list):
        for child in value:
            result.update(_auth_context_keys(child, parent, depth + 1))
    return result


def _remember_auth_context(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    token = (message.headers or {}).get(MYTHIC_AUTH_CONTEXT_HEADER)
    if not isinstance(token, str) or not token:
        return
    try:
        keys = _auth_context_keys(ujson.loads(message.body))
    except ValueError:
        return
    now = time.time()
    for key, (_, expires, _) in list(_request_auth_contexts.items()):
        if expires <= now:
            _request_auth_contexts.pop(key, None)
    route = getattr(message, "routing_key", "") or ""
    for key in keys:
        is_operation = key.startswith("operation_id:")
        if is_operation and route != "container_on_start" and not route.endswith("_container_on_start"):
            continue
        existing = _request_auth_contexts.get(key)
        if existing and existing[0] != token and not is_operation:
            _request_auth_contexts[key] = (existing[0], now + AUTH_CONTEXT_CACHE_TTL, True)
            continue
        if existing is None and len(_request_auth_contexts) >= AUTH_CONTEXT_CACHE_LIMIT:
            continue
        _request_auth_contexts[key] = (token, now + AUTH_CONTEXT_CACHE_TTL, False)


def _cached_auth_context(body: bytes) -> Optional[str]:
    active = _current_auth_context.get()
    if active:
        return active
    try:
        keys = _auth_context_keys(ujson.loads(body))
    except ValueError:
        return None
    now = time.time()
    specific_keys = {key for key in keys if not key.startswith("operation_id:")}
    selected_keys = specific_keys or {key for key in keys if key.startswith("operation_id:")}
    context_tokens: set[str] = set()
    for key in selected_keys:
        entry = _request_auth_contexts.get(key)
        if entry is None:
            continue
        token, expires, ambiguous = entry
        if expires <= now:
            _request_auth_contexts.pop(key, None)
            continue
        if ambiguous:
            raise ValueError(f"message identifier {key} has ambiguous RabbitMQ auth contexts")
        context_tokens.add(token)
    if len(context_tokens) > 1:
        raise ValueError("message identifiers resolve to different RabbitMQ auth contexts")
    return next(iter(context_tokens), None)


def _signed_message(queue: str, body: bytes, **kwargs) -> aio_pika.Message:
    principal = settings.get("mythic_container_principal", "")
    token_hex = settings.get("mythic_container_auth_token", "")
    rabbitmq_user = settings.get("rabbitmq_user", "mythic_user")
    if not isinstance(principal, str) or not principal or principal != principal.strip().lower():
        raise ValueError("MYTHIC_CONTAINER_PRINCIPAL is missing or non-canonical")
    try:
        secret = bytes.fromhex(token_hex)
    except (TypeError, ValueError) as exc:
        raise ValueError("MYTHIC_CONTAINER_AUTH_TOKEN is missing or invalid") from exc
    if len(secret) != hashlib.sha256().digest_size:
        raise ValueError("MYTHIC_CONTAINER_AUTH_TOKEN is missing or invalid")
    timestamp = int(time.time())
    nonce = secrets.token_hex(24)
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"v1\n{principal}\n{queue}\n{timestamp}\n{nonce}\n{body_hash}"
    signature = hmac.new(secret, canonical.encode(), hashlib.sha256).hexdigest()
    headers = dict(kwargs.pop("headers", {}) or {})
    headers.update({
        MYTHIC_CONTAINER_PRINCIPAL_HEADER: principal,
        MYTHIC_CONTAINER_TIMESTAMP_HEADER: timestamp,
        MYTHIC_CONTAINER_NONCE_HEADER: nonce,
        MYTHIC_CONTAINER_SIGNATURE_HEADER: signature,
    })
    auth_context = _cached_auth_context(body)
    if auth_context:
        headers[MYTHIC_AUTH_CONTEXT_HEADER] = auth_context
    return aio_pika.Message(body=body, user_id=rabbitmq_user, headers=headers, **kwargs)


def _container_reply_routing_key(correlation_id: str) -> str:
    principal = settings.get("mythic_container_principal", "")
    if not isinstance(principal, str) or not principal or principal != principal.strip().lower():
        raise ValueError("MYTHIC_CONTAINER_PRINCIPAL is missing or non-canonical")
    if not correlation_id:
        raise ValueError("RabbitMQ reply correlation ID is empty")
    return f"{principal}.reply.{correlation_id}"


def _container_telemetry_routing_key(routing_key: str) -> str:
    principal = settings.get("mythic_container_principal", "")
    if not isinstance(principal, str) or not principal or principal != principal.strip().lower():
        raise ValueError("MYTHIC_CONTAINER_PRINCIPAL is missing or non-canonical")
    return f"{principal}.{routing_key}"


async def messageProcessThread(message: aio_pika.abc.AbstractIncomingMessage,
                               trueFunction: Callable[[bytes], Awaitable[None]]) -> None:
    try:
        _remember_auth_context(message)
        incoming_token = (message.headers or {}).get(MYTHIC_AUTH_CONTEXT_HEADER)
        context_token = _current_auth_context.set(incoming_token if isinstance(incoming_token, str) else None)
        logger.debug(f"Ack direct call to {message.routing_key}")
        await message.ack()
        try:
            await trueFunction(message.body)
        finally:
            _current_auth_context.reset(context_token)
    except Exception as d:
        logger.exception(f"inner error: {d}")
        await message.nack(requeue=True)


async def directExchangeCallback(message: aio_pika.abc.AbstractIncomingMessage,
                                 trueFunction: Callable[[bytes], Awaitable[None]]) -> None:
    # run async supplied function as background thread
    logger.debug(f"Got direct call to {message.routing_key}")
    #async with message.process(ignore_processed=True) as messageContext:
        # _thread = Thread(target=asyncio.run,
        #                 args=(messageProcessThread(message=messageContext, trueFunction=trueFunction),))
        # _thread.start()  # start thread
    #    await messageProcessThread(message=messageContext, trueFunction=trueFunction)
    await messageProcessThread(message=message, trueFunction=trueFunction)


async def messageProcessRPCThread(message: aio_pika.abc.AbstractIncomingMessage,
                                  trueFunction: Callable[[bytes], Awaitable[bytes]]) -> bytes:
    try:
        _remember_auth_context(message)
        incoming_token = (message.headers or {}).get(MYTHIC_AUTH_CONTEXT_HEADER)
        context_token = _current_auth_context.set(incoming_token if isinstance(incoming_token, str) else None)
        try:
            response = await trueFunction(message.body)
        finally:
            _current_auth_context.reset(context_token)
        #logger.info(f"rpc response: {response}\nrequest: {message.body}")
        return response
    except Exception as d:
        logger.exception(f"rpc inner error: {d}")
        return f"rpc error: {d}".encode()


async def rpcExchangeCallback(message: aio_pika.abc.AbstractIncomingMessage,
                              trueFunction: Callable[[bytes], Awaitable[any]]) -> None:
    # run async supplied function as background thread
    async with message.process(ignore_processed=True) as messageContext:
        # _thread = Thread(target=asyncio.run,
        #                 args=(messageProcessThread(message=messageContext, trueFunction=trueFunction),))
        # _thread.start()  # start thread
        logger.debug(f"Got RPC call to {message.routing_key}, correlation_id: {message.correlation_id}")
        response = await messageProcessRPCThread(message=messageContext, trueFunction=trueFunction)
        await mythic_container.RabbitmqConnection.ReplyMessage(response=response, message=messageContext)


class rabbitmqConnectionClass:
    conn: aio_pika.robust_connection.AbstractRobustConnection = None
    futures: MutableMapping[str, asyncio.Future] = {}

    def __init__(self):
        pass

    async def async_init(self):
        self.conn = await self.GetConnection()
        return self

    def __await__(self):
        return self.async_init().__await__()

    async def GetConnection(self) -> aio_pika.robust_connection.AbstractRobustConnection:
        async with mutex:
            while True:
                try:
                    if self.conn is not None and not self.conn.is_closed:
                        return self.conn
                    logger.info("[*] Trying to connect to rabbitmq at: "
                                 + settings.get("rabbitmq_host", "127.0.0.1")
                                 + ":"
                                 + str(settings.get("rabbitmq_port", 5672))
                                 + f", with user: {settings.get('rabbitmq_user', 'mythic_user')}"
                                 + f", with vhost: {settings.get('rabbitmq_vhost', 'mythic_vhost')}"
                                 )
                    self.conn = await aio_pika.connect_robust(
                        host=settings.get("rabbitmq_host", "127.0.0.1"),
                        port=settings.get("rabbitmq_port", 5672),
                        login=settings.get("rabbitmq_user", "mythic_user"),
                        password=settings.get("rabbitmq_password", "rabbitmq_password"),
                        virtualhost=settings.get("rabbitmq_vhost", "mythic_vhost"),
                        timeout=failedConnectTimeout,
                        heartbeat=30,
                        reconnect_interval=2,
                        retry_delay=2.0,
                        max_attempts=5,
                    )
                    logger.critical("[+] Successfully connected to rabbitmq")
                    return self.conn
                except Exception as e:
                    logger.error(f"[-] Failed to connect to rabbitmq: {e}")
                    await asyncio.sleep(failedConnectRetryDelay)

    async def SendMessage(self, queue: str, body: bytes):
        while True:
            try:
                connection = await self.GetConnection()
                async with connection.channel(publisher_confirms=True,
                                              on_return_raises=True) as chan:
                    exchange = await chan.get_exchange("mythic_exchange", ensure=False)
                    message = _signed_message(queue, body,
                                              content_type="application/json")
                    await exchange.publish(
                        message=message,
                        routing_key=queue,
                        timeout=failedConnectRetryDelay,
                        mandatory=True,
                        immediate=False,
                    )
                    return
            except Exception as e:
                logger.exception(f"[-] failed to send message: {e}")
                return

    async def SendDictDirectMessage(self, queue: str, body: dict) -> None:
        #logger.debug(f"Sending Direct msg to {queue}: {body}")
        return await self.SendMessage(queue=queue, body=ujson.dumps(body).encode())

    async def SendRPCMessage(self, queue: str, body: bytes) -> dict:
        try:
            while True:
                correlation_id = str(uuid.uuid4())
                future = asyncio.get_event_loop().create_future()
                self.futures[correlation_id] = future
                logger.debug(f"Sending RPC message to {queue}, correlation_id: {correlation_id}")
                connection = await self.GetConnection()
                async with connection.channel(on_return_raises=True) as chan:
                    exchange = await chan.get_exchange("mythic_exchange", ensure=False)
                    reply_exchange = await chan.get_exchange(MYTHIC_RPC_REPLY_EXCHANGE, ensure=False)
                    reply_routing_key = _container_reply_routing_key(correlation_id)
                    callback_queue = await chan.declare_queue(
                        name="", durable=False, auto_delete=True, exclusive=True
                    )
                    await callback_queue.bind(reply_exchange, routing_key=reply_routing_key)
                    await callback_queue.consume(self.on_response,
                                                 no_ack=True)
                    message = _signed_message(queue, body,
                                              content_type="application/json",
                                              reply_to=reply_routing_key,
                                              correlation_id=correlation_id)
                    # make sure the queue exists first before we try to send to it
                    try:
                        await exchange.publish(
                            message=message,
                            routing_key=queue,
                            mandatory=True,
                            immediate=False,
                            timeout=10
                        )
                    except asyncio.TimeoutError:
                        # cancel the current future and move on to try again
                        future.cancel()
                        self.futures.pop(message.correlation_id, None)
                        logger.error(f"hit timeout waiting for RPC response in {queue} for correlation_id: {message.correlation_id}, retrying...")
                        continue
                    except Exception as err:
                        future.cancel()
                        self.futures.pop(message.correlation_id, None)
                        logger.error(f"hit error trying to send RPC message in {queue} for correlation_id: {message.correlation_id}, retrying...:\n{err}")
                        await asyncio.sleep(5)
                        continue
                    logger.debug(f"published RPC message to {queue}, correlation id: {message.correlation_id}")
                    try:
                        result = await asyncio.wait_for(future, timeout=10)
                        logger.debug(f"got RPC result to {queue}, correlation id: {message.correlation_id}")
                        return result
                    except asyncio.TimeoutError:
                        # cancel the current future and move on to try again
                        future.cancel()
                        logger.error(f"hit timeout waiting for RPC response on {queue} for correlation_id {message.correlation_id}, retrying...")
                    except Exception as sendError:
                        logger.error(f"got error on {queue} for correlation_id {message.correlation_id}:\n{sendError}")
                        await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"[-] failed to send rpc message to {queue}: {e}")
            return {}

    def on_response(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        try:
            #logger.debug(f"got on_response for correlation_id: {message.correlation_id}")
            if message.correlation_id is None:
                logger.error(f"Bad message {message!r}")
                return

            future: asyncio.Future = self.futures.pop(message.correlation_id, None)
            if future:
                try:
                    if future.cancelled():
                        logger.debug(f"got response for {message.correlation_id}, but it was cancelled")
                    else:
                        future.set_result(ujson.loads(message.body))
                        logger.debug(f"got response for {message.correlation_id}")

                except Exception as fe:
                    logger.exception(f"Failed to process response as json: {fe}")
                    future.set_result({})
            else:
                logger.error(
                    f"Failed to handle response: unknown correlation_id\nmessage: {message}\nbody:{message.body}\nfutures:{self.futures}")
        except Exception as e:
            logger.exception(
                f"Failed to handle response: {e}\nmessage: {message}\nbody:{message.body}\nfutures:{self.futures}")

    async def SendRPCDictMessage(self, queue: str, body: dict) -> dict:
        #logger.debug(f"Sending RPC msg: {body}")
        return await self.SendRPCMessage(queue=queue, body=ujson.dumps(body).encode())

    async def ReplyMessage(self, response: bytes, message: aio_pika.abc.AbstractIncomingMessage):
        try:
            connection = await self.GetConnection()
            async with connection.channel(on_return_raises=True) as chan:
                exchange = await chan.get_exchange(MYTHIC_RPC_REPLY_EXCHANGE, ensure=False)
                newMessage = aio_pika.Message(
                    body=response,
                    content_type="application/json",
                    correlation_id=message.correlation_id)

                await exchange.publish(
                    newMessage,
                    routing_key=_container_reply_routing_key(message.correlation_id),
                    mandatory=False
                )
                logger.debug(f"Send reply for correlation_id: {message.correlation_id}")

        except Exception as e:
            logger.exception(f"[-] failed to send reply message: {e}")
            pass

    async def ReceiveFromMythicDirectExchange(self, queue: str, routing_key: str,
                                              handler: Coroutine[any, any, None]):
        while True:
            try:
                connection = await self.GetConnection()
                async with connection.channel() as chan:
                    exchange = await chan.get_exchange("mythic_exchange", ensure=False)
                    q = await chan.declare_queue(
                        name=queue,
                        durable=False,
                        auto_delete=True,
                        exclusive=False,
                    )
                    await q.bind(
                        exchange=exchange,
                        routing_key=routing_key,
                    )
                    await q.consume(
                        callback=partial(directExchangeCallback, trueFunction=handler),
                    )
                    logger.info(f"[*] started listening for messages on {queue}")
                    try:
                        await asyncio.Future()
                        logger.error(f"asyncio.Future() finished in ReceiveFromMythicDirectExchange for {queue}")
                    except Exception as directException:
                        logger.exception(f"[-] exception trying to listen for direct messages on {queue}\n{directException}")
            except aiormq.exceptions.ChannelLockedResource:
                logger.error(f"[-] Another instance of this service, {queue.split('_')[0]}, is running, failed to start, trying again...")
                await asyncio.sleep(failedConnectRetryDelay)
            except Exception as e:
                logger.exception(f"[-] stopped listening for messages on {queue}, {e}")
                await asyncio.sleep(failedConnectRetryDelay)

    async def ReceiveFromRPCQueue(self, queue: str, routing_key: str, handler: Coroutine[any, any, None]):
        while True:
            try:
                connection = await self.GetConnection()
                async with connection.channel() as chan:
                    exchange = await chan.get_exchange("mythic_exchange", ensure=False)
                    q = await chan.declare_queue(
                        name=queue,
                        durable=False,
                        auto_delete=True,
                        exclusive=True,
                    )
                    await q.bind(
                        exchange=exchange,
                        routing_key=routing_key,
                    )
                    await q.consume(
                        callback=partial(rpcExchangeCallback, trueFunction=handler),
                    )
                    logger.info(f"[*] started listening for messages on {queue}")
                    try:
                        await asyncio.Future()
                    finally:
                        logger.error(f"asyncio.Future() finished in ReceiveFromRPCQueue for queue {queue}")
            except aiormq.exceptions.ChannelLockedResource:
                logger.error(f"[-] Another instance of this service, {queue.split('_')[0]}, is running, failed to start, trying again...")
                await asyncio.sleep(failedConnectRetryDelay)
            except Exception as e:
                logger.exception(f"[-] stopped listening for messages on {queue}, {e}")
                await asyncio.sleep(failedConnectRetryDelay)

    async def ReceiveFromMythicDirectTopicExchange(self, queue: str, routing_key: str,
                                                   handler: Coroutine[any, any, None]):
        while True:
            try:
                connection = await self.GetConnection()
                async with connection.channel() as chan:
                    exchange = await chan.get_exchange("mythic_topic_exchange", ensure=False)
                    q = await chan.declare_queue(
                        name="",
                        durable=False,
                        auto_delete=True,
                        exclusive=False,
                    )
                    scoped_routing_key = _container_telemetry_routing_key(routing_key)
                    await q.bind(
                        exchange=exchange,
                        routing_key=scoped_routing_key,
                    )
                    await q.consume(
                        callback=partial(directExchangeCallback, trueFunction=handler)
                    )
                    logger.info(f"[*] started listening for messages on {queue}")
                    try:
                        await asyncio.Future()
                        logger.error(f"asyncio.Future() finished in ReceiveFromMythicDirectTopicExchange for {queue}")
                    except Exception as directException:
                        logger.exception(f"[-] exception trying to listen for direct messages on {queue}\n{directException}")
            except Exception as e:
                logger.exception(f"[-] stopped listening for messages on {queue}, {e}")
                await asyncio.sleep(failedConnectRetryDelay)
