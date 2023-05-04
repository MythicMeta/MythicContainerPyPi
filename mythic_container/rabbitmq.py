import concurrent.futures

import aiormq.exceptions

from .logging import logger
import aio_pika
import asyncio
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


async def messageProcessThread(message: aio_pika.abc.AbstractIncomingMessage,
                               trueFunction: Callable[[bytes], Awaitable[None]]) -> None:
    try:
        await trueFunction(message.body)
    except Exception as d:
        logger.exception(f"inner error: {d}")


async def directExchangeCallback(message: aio_pika.abc.AbstractIncomingMessage,
                                 trueFunction: Callable[[bytes], Awaitable[None]]) -> None:
    # run async supplied function as background thread
    logger.debug(f"Got direct call to {message.routing_key}")
    async with message.process() as messageContext:
        # _thread = Thread(target=asyncio.run,
        #                 args=(messageProcessThread(message=messageContext, trueFunction=trueFunction),))
        # _thread.start()  # start thread
        await messageProcessThread(message=messageContext, trueFunction=trueFunction)


async def messageProcessRPCThread(message: aio_pika.abc.AbstractIncomingMessage,
                                  trueFunction: Callable[[bytes], Awaitable[bytes]]) -> bytes:
    try:
        response = await trueFunction(message.body)
        #logger.info(f"rpc response: {response}\nrequest: {message.body}")
        return response
    except Exception as d:
        logger.exception(f"rpc inner error: {d}")
        return f"rpc error: {d}".encode()


async def rpcExchangeCallback(message: aio_pika.abc.AbstractIncomingMessage,
                              trueFunction: Callable[[bytes], Awaitable[any]]) -> None:
    # run async supplied function as background thread
    async with message.process() as messageContext:
        # _thread = Thread(target=asyncio.run,
        #                 args=(messageProcessThread(message=messageContext, trueFunction=trueFunction),))
        # _thread.start()  # start thread
        logger.debug(f"Got RPC call to {message.routing_key}")
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
                                 )
                    logger.debug(f"connecting with password: {settings.get('rabbitmq_password', 'rabbitmq_password')}...")
                    self.conn = await aio_pika.connect_robust(
                        host=settings.get("rabbitmq_host", "127.0.0.1"),
                        port=settings.get("rabbitmq_port", 5672),
                        login="mythic_user",
                        password=settings.get("rabbitmq_password", "rabbitmq_password"),
                        virtualhost="mythic_vhost",
                        timeout=failedConnectTimeout,
                    )
                    logger.info("[+] Successfully connected to rabbitmq")
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
                    exchange = await chan.declare_exchange("mythic_exchange",
                                                           durable=True,
                                                           auto_delete=True)
                    message = aio_pika.Message(body=body,
                                               content_type="application/json")
                    await exchange.publish(
                        message=message,
                        routing_key=queue,
                        timeout=failedConnectRetryDelay,
                        mandatory=True,
                        immediate=False)
                    return
            except Exception as e:
                logger.exception(f"[-] failed to send message: {e}")
                return

    async def SendDictDirectMessage(self, queue: str, body: dict) -> None:
        #logger.debug(f"Sending Direct msg to {queue}: {body}")
        return await self.SendMessage(queue=queue, body=ujson.dumps(body).encode())

    async def SendRPCMessage(self, queue: str, body: bytes) -> dict:
        future = asyncio.get_event_loop().create_future()
        logger.debug(f"Sending RPC message to {queue}")
        try:
            correlation_id = str(uuid.uuid4())
            self.futures[correlation_id] = future
            while True:
                connection = await self.GetConnection()
                async with connection.channel(on_return_raises=True) as chan:
                    exchange = await chan.declare_exchange("mythic_exchange",
                                                           durable=True,
                                                           auto_delete=True)
                    callback_queue = await chan.declare_queue(name="amq.rabbitmq.reply-to",)
                    await callback_queue.consume(self.on_response,
                                                 no_ack=True)
                    message = aio_pika.Message(body=body,
                                               content_type="application/json",
                                               reply_to=callback_queue.name,
                                               correlation_id=correlation_id)
                    # make sure the queue exists first before we try to send to it
                    await exchange.publish(
                        message=message,
                        routing_key=queue,
                        mandatory=True,
                        immediate=False,
                        timeout=20
                    )
                    result = await future
                    return result
        except Exception as e:
            logger.error(f"[-] failed to send rpc message to {queue}: {e}")
            future.set_result({})
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
                    future.set_result(ujson.loads(message.body))
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
                exchange = chan.default_exchange
                newMessage = aio_pika.Message(
                    body=response,
                    content_type="application/json",
                    correlation_id=message.correlation_id)

                await exchange.publish(
                    newMessage,
                    routing_key=message.reply_to,
                    mandatory=False
                )

        except Exception as e:
            logger.exception(f"[-] failed to send reply message: {e}")
            pass

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
                        callback=partial(directExchangeCallback, trueFunction=handler)
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
                        durable=False,
                        auto_delete=True,
                        exclusive=True,
                    )
                    await q.bind(
                        exchange=exchange,
                        routing_key=routing_key,
                    )
                    await q.consume(
                        callback=partial(rpcExchangeCallback, trueFunction=handler)
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
                        routing_key=queue,
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
