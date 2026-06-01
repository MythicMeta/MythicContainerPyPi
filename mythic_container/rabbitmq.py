import concurrent.futures
import contextvars

import aiormq.exceptions

from .logging import logger
import aio_pika
import base64
import mythic_container
from .config import settings
from collections.abc import Callable, Awaitable
from typing import Coroutine
import ujson
import asyncio
from functools import partial
import uuid
from typing import MutableMapping


mutex = asyncio.Lock()

failedConnectRetryDelay = 5
failedConnectTimeout = 1
RPC_TIMEOUT = 10
RPC_RETRY_POLICY_RETRY_ON_TIMEOUT = 0
RPC_RETRY_POLICY_NO_RETRY_ON_TIMEOUT = 1
RPC_RETRY_POLICY_CUSTOM_TIMEOUT = 2
MYTHIC_AUTH_CONTEXT_HEADER = "mythic-auth-context"
_rabbitmq_auth_context = contextvars.ContextVar("mythic_rabbitmq_auth_context", default=None)


def GetRabbitMQAuthContext() -> str | None:
    return _rabbitmq_auth_context.get()


def SetRabbitMQAuthContext(auth_context: str | None):
    return _rabbitmq_auth_context.set(auth_context)


def ResetRabbitMQAuthContext(token) -> None:
    _rabbitmq_auth_context.reset(token)


def _get_message_auth_context(message: aio_pika.abc.AbstractIncomingMessage) -> str | None:
    headers = message.headers or {}
    auth_context = headers.get(MYTHIC_AUTH_CONTEXT_HEADER)
    if isinstance(auth_context, bytes):
        auth_context = auth_context.decode()
    if auth_context:
        return str(auth_context)
    return None


def _headers_with_current_auth_context() -> dict | None:
    auth_context = GetRabbitMQAuthContext()
    if auth_context:
        return {MYTHIC_AUTH_CONTEXT_HEADER: auth_context}
    return None


async def messageProcessThread(message: aio_pika.abc.AbstractIncomingMessage,
                               trueFunction: Callable[[bytes], Awaitable[None]]) -> None:
    token = SetRabbitMQAuthContext(_get_message_auth_context(message))
    try:
        logger.debug(f"Ack direct call to {message.routing_key}")
        await message.ack()
        await trueFunction(message.body)
    except Exception as d:
        logger.exception(f"inner error: {d}")
        await message.nack(requeue=True)
    finally:
        ResetRabbitMQAuthContext(token)


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
    token = SetRabbitMQAuthContext(_get_message_auth_context(message))
    try:
        response = await trueFunction(message.body)
        #logger.info(f"rpc response: {response}\nrequest: {message.body}")
        return response
    except Exception as d:
        logger.exception(f"rpc inner error: {d}")
        return f"rpc error: {d}".encode()
    finally:
        ResetRabbitMQAuthContext(token)


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
        self.conn = None
        self.futures = {}
        self.publisher_lock = asyncio.Lock()
        self.publisher_channel = None
        self.publisher_exchange = None
        self.rpc_lock = asyncio.Lock()
        self.rpc_channel = None
        self.rpc_exchange = None
        self.rpc_exchanges = set()

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
                    logger.debug(f"connecting with password: {settings.get('rabbitmq_password', 'rabbitmq_password')}...")
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

    async def _get_publisher_channel_locked(self):
        if self.publisher_channel is not None and not self.publisher_channel.is_closed:
            return self.publisher_channel, self.publisher_exchange
        connection = await self.GetConnection()
        self.publisher_channel = await connection.channel(
            publisher_confirms=True,
            on_return_raises=True,
        )
        self.publisher_exchange = await self.publisher_channel.declare_exchange(
            "mythic_exchange",
            durable=True,
            auto_delete=True,
        )
        return self.publisher_channel, self.publisher_exchange

    async def _reset_publisher_channel_locked(self):
        if self.publisher_channel is not None and not self.publisher_channel.is_closed:
            try:
                await self.publisher_channel.close()
            except Exception as e:
                logger.debug(f"failed to close publisher channel: {e}")
        self.publisher_channel = None
        self.publisher_exchange = None

    async def SendMessage(self, queue: str, body: bytes):
        for _ in range(3):
            try:
                async with self.publisher_lock:
                    _channel, exchange = await self._get_publisher_channel_locked()
                    message = aio_pika.Message(body=body,
                                               content_type="application/json",
                                               headers=_headers_with_current_auth_context())
                    await exchange.publish(
                        message=message,
                        routing_key=queue,
                        timeout=failedConnectRetryDelay,
                        mandatory=True,
                        immediate=False,
                    )
                return
            except Exception as e:
                logger.exception(f"[-] failed to send message to {queue}: {e}")
                async with self.publisher_lock:
                    await self._reset_publisher_channel_locked()
                await asyncio.sleep(failedConnectRetryDelay)
        logger.error(f"[-] failed 3 times to send message to {queue}")

    async def SendDictDirectMessage(self, queue: str, body: dict) -> None:
        #logger.debug(f"Sending Direct msg to {queue}: {body}")
        return await self.SendMessage(queue=queue, body=ujson.dumps(body).encode())

    def _get_rpc_timeout(self, retry_policy: int) -> int:
        if retry_policy == RPC_RETRY_POLICY_CUSTOM_TIMEOUT:
            custom_timeout = settings.get("custom_rpc_timeout", 0)
            if custom_timeout and int(custom_timeout) > 0:
                return int(custom_timeout)
        return RPC_TIMEOUT

    async def _get_rpc_client_locked(self):
        if self.rpc_channel is not None and not self.rpc_channel.is_closed:
            if "mythic_exchange" not in self.rpc_exchanges:
                self.rpc_exchange = await self.rpc_channel.declare_exchange(
                    "mythic_exchange",
                    durable=True,
                    auto_delete=True,
                )
                self.rpc_exchanges.add("mythic_exchange")
            return self.rpc_channel, self.rpc_exchange
        connection = await self.GetConnection()
        self.rpc_channel = await connection.channel(
            publisher_confirms=True,
            on_return_raises=True,
        )
        callback_queue = await self.rpc_channel.declare_queue(name="amq.rabbitmq.reply-to")
        await callback_queue.consume(self.on_response, no_ack=True)
        self.rpc_exchange = await self.rpc_channel.declare_exchange(
            "mythic_exchange",
            durable=True,
            auto_delete=True,
        )
        self.rpc_exchanges = {"mythic_exchange"}
        return self.rpc_channel, self.rpc_exchange

    async def _reset_rpc_client_locked(self, error: Exception):
        for correlation_id, future in list(self.futures.items()):
            if not future.done():
                future.set_exception(error)
            self.futures.pop(correlation_id, None)
        if self.rpc_channel is not None and not self.rpc_channel.is_closed:
            try:
                await self.rpc_channel.close()
            except Exception as e:
                logger.debug(f"failed to close rpc channel: {e}")
        self.rpc_channel = None
        self.rpc_exchange = None
        self.rpc_exchanges = set()

    async def _publish_rpc_message(self, queue: str, body: bytes, correlation_id: str, future: asyncio.Future):
        async with self.rpc_lock:
            _channel, exchange = await self._get_rpc_client_locked()
            self.futures[correlation_id] = future
            message = aio_pika.Message(
                body=body,
                content_type="application/json",
                reply_to="amq.rabbitmq.reply-to",
                correlation_id=correlation_id,
                headers=_headers_with_current_auth_context(),
            )
            try:
                await exchange.publish(
                    message=message,
                    routing_key=queue,
                    mandatory=True,
                    immediate=False,
                    timeout=RPC_TIMEOUT,
                )
            except Exception as err:
                self.futures.pop(correlation_id, None)
                await self._reset_rpc_client_locked(err)
                raise

    async def SendRPCMessage(self, queue: str, body: bytes,
                             retry_policy: int = RPC_RETRY_POLICY_RETRY_ON_TIMEOUT) -> dict:
        final_error = None
        timeout = self._get_rpc_timeout(retry_policy)
        for _ in range(3):
            correlation_id = str(uuid.uuid4())
            future = asyncio.get_event_loop().create_future()
            logger.debug(f"Sending RPC message to {queue}, correlation_id: {correlation_id}")
            try:
                await self._publish_rpc_message(queue=queue, body=body, correlation_id=correlation_id, future=future)
                logger.debug(f"published RPC message to {queue}, correlation id: {correlation_id}")
            except Exception as err:
                final_error = err
                logger.error(f"hit error trying to send RPC message in {queue} for correlation_id: {correlation_id}, retrying:\n{err}")
                if not future.done():
                    future.cancel()
                await asyncio.sleep(failedConnectRetryDelay)
                continue
            try:
                result = await asyncio.wait_for(future, timeout=timeout)
                logger.debug(f"got RPC result to {queue}, correlation id: {correlation_id}")
                return result
            except asyncio.TimeoutError as err:
                final_error = err
                self.futures.pop(correlation_id, None)
                if not future.done():
                    future.cancel()
                logger.error(f"hit timeout waiting for RPC response on {queue} for correlation_id {correlation_id}")
                if retry_policy != RPC_RETRY_POLICY_RETRY_ON_TIMEOUT:
                    return {}
            except Exception as sendError:
                final_error = sendError
                self.futures.pop(correlation_id, None)
                logger.error(f"got error on {queue} for correlation_id {correlation_id}:\n{sendError}")
                if retry_policy != RPC_RETRY_POLICY_RETRY_ON_TIMEOUT:
                    return {}
                await asyncio.sleep(failedConnectRetryDelay)
        logger.error(f"[-] failed 3 times to send rpc message to {queue}: {final_error}")
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

    async def SendRPCDictMessage(self, queue: str, body: dict,
                                 retry_policy: int = RPC_RETRY_POLICY_RETRY_ON_TIMEOUT) -> dict:
        #logger.debug(f"Sending RPC msg: {body}")
        return await self.SendRPCMessage(queue=queue, body=ujson.dumps(body).encode(), retry_policy=retry_policy)

    async def ReplyMessage(self, response: bytes, message: aio_pika.abc.AbstractIncomingMessage):
        try:
            await message.channel.basic_publish(
                body=response,
                exchange="",
                routing_key=message.reply_to,
                properties=aiormq.spec.Basic.Properties(
                    content_type="application/json",
                    correlation_id=message.correlation_id,
                ),
                mandatory=False,
            )
            logger.debug(f"Send reply for correlation_id: {message.correlation_id}")

        except Exception as e:
            logger.exception(f"[-] failed to send reply message: {e}")
            raise

    async def ReceiveFromMythicDirectExchange(self, queue: str, routing_key: str,
                                              handler: Coroutine[any, any, None]):
        while True:
            try:
                connection = await self.GetConnection()
                async with connection.channel() as chan:
                    exchange = await chan.declare_exchange(
                        name="mythic_exchange",
                        type="direct",
                        durable=True,
                        auto_delete=True,
                        internal=False,
                    )
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
                    exchange = await chan.declare_exchange(
                        name="mythic_exchange",
                        type="direct",
                        durable=True,
                        auto_delete=True,
                        internal=False,

                    )
                    q = await chan.declare_queue(
                        name=queue,
                        durable=True,
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
                    exchange = await chan.declare_exchange(
                        name="mythic_topic_exchange",
                        type="topic",
                        durable=True,
                        auto_delete=True,
                        internal=False,
                    )
                    q = await chan.declare_queue(
                        name="",
                        durable=False,
                        auto_delete=True,
                        exclusive=False,
                    )
                    await q.bind(
                        exchange=exchange,
                        routing_key=routing_key,
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
