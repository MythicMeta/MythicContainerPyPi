import concurrent.futures

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


async def messageProcessThread(message: aio_pika.abc.AbstractIncomingMessage,
                               trueFunction: Callable[[bytes], Awaitable[None]]) -> None:
    try:
        logger.debug("Ack direct call to %s", message.routing_key)
        await message.ack()
        await trueFunction(message.body)
    except:
        logger.exception("inner error")
        await message.nack(requeue=True)


async def directExchangeCallback(message: aio_pika.abc.AbstractIncomingMessage,
                                 trueFunction: Callable[[bytes], Awaitable[None]]) -> None:
    # run async supplied function as background thread
    logger.debug("Got direct call to %s", message.routing_key)
    #async with message.process(ignore_processed=True) as messageContext:
        # _thread = Thread(target=asyncio.run,
        #                 args=(messageProcessThread(message=messageContext, trueFunction=trueFunction),))
        # _thread.start()  # start thread
    #    await messageProcessThread(message=messageContext, trueFunction=trueFunction)
    await messageProcessThread(message=message, trueFunction=trueFunction)


async def messageProcessRPCThread(message: aio_pika.abc.AbstractIncomingMessage,
                                  trueFunction: Callable[[bytes], Awaitable[bytes]]) -> bytes:
    try:
        response = await trueFunction(message.body)
        #logger.info(f"rpc response: {response}\nrequest: {message.body}")
        return response
    except Exception as d:
        logger.exception("rpc inner error")
        return f"rpc error: {d}".encode()


async def rpcExchangeCallback(message: aio_pika.abc.AbstractIncomingMessage,
                              trueFunction: Callable[[bytes], Awaitable[any]]) -> None:
    # run async supplied function as background thread
    async with message.process(ignore_processed=True) as messageContext:
        # _thread = Thread(target=asyncio.run,
        #                 args=(messageProcessThread(message=messageContext, trueFunction=trueFunction),))
        # _thread.start()  # start thread
        logger.debug("Got RPC call to %s, correlation_id: %s", message.routing_key, message.correlation_id)
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
                    logger.info("[*] Trying to connect to rabbitmq at: %s:%s",
                                settings.get("rabbitmq_host", "127.0.0.1"),
                                settings.get("rabbitmq_port", 5672))
                    logger.debug("connecting with password: %s...", settings.get('rabbitmq_password', 'rabbitmq_password'))
                    self.conn = await aio_pika.connect_robust(
                        host=settings.get("rabbitmq_host", "127.0.0.1"),
                        port=settings.get("rabbitmq_port", 5672),
                        login="mythic_user",
                        password=settings.get("rabbitmq_password", "rabbitmq_password"),
                        virtualhost="mythic_vhost",
                        timeout=failedConnectTimeout,
                        heartbeat=30,
                        reconnect_interval=2,
                        retry_delay=2.0,
                        max_attempts=3,
                    )
                    logger.critical("[+] Successfully connected to rabbitmq")
                    return self.conn
                except:
                    logger.exception("[-] Failed to connect to rabbitmq")
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
                        immediate=False,
                    )
                    return
            except:
                logger.exception("[-] failed to send message")
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
                logger.debug("Sending RPC message to %s, correlation_id: %s", queue, correlation_id)
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
                        logger.error("hit timeout waiting for RPC response in %s for correlation_id: %s, retrying...",
                                     queue, message.correlation_id)
                        continue
                    except:
                        future.cancel()
                        self.futures.pop(message.correlation_id, None)
                        logger.exception("hit error trying to send RPC message in %s for correlation_id: %s, retrying...",
                                         queue, message.correlation_id)
                        await asyncio.sleep(5)
                        continue
                    logger.debug("published RPC message to %s, correlation id: %s", queue, message.correlation_id)
                    try:
                        result = await asyncio.wait_for(future, timeout=10)
                        logger.debug("got RPC result to %s, correlation id: %s", queue, message.correlation_id)
                        return result
                    except asyncio.TimeoutError:
                        # cancel the current future and move on to try again
                        future.cancel()
                        logger.error("hit timeout waiting for RPC response on %s for correlation_id %s, retrying...",
                                     queue, message.correlation_id)
                    except Exception as sendError:
                        logger.exception("got error on %s for correlation_id %s", queue, message.correlation_id)
                        await asyncio.sleep(5)

        except:
            logger.error("[-] failed to send rpc message to %s", queue)
            return {}

    def on_response(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        try:
            #logger.debug(f"got on_response for correlation_id: {message.correlation_id}")
            if message.correlation_id is None:
                logger.error("Bad message %s", repr(message))
                return

            future: asyncio.Future = self.futures.pop(message.correlation_id, None)
            if future:
                try:
                    if future.cancelled():
                        logger.debug("got response for %s, but it was cancelled", message.correlation_id)
                    else:
                        future.set_result(ujson.loads(message.body))
                        logger.debug("got response for %s", message.correlation_id)

                except Exception:
                    logger.exception("Failed to process response as json")
                    future.set_result({})
            else:
                logger.error("Failed to handle response: unknown correlation_id\nmessage: %s\nbody: %s\nfutures: %s",
                             message, message.body, self.futures)
        except Exception as e:
            logger.exception("Failed to handle response: %s\nmessage: %s\nbody:%s\nfutures:%s",
                             e, message, message.body, self.futures)

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
                logger.debug("Send reply for correlation_id: %s", message.correlation_id)

        except:
            logger.exception("[-] failed to send reply message")
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
                        callback=partial(directExchangeCallback, trueFunction=handler),
                    )
                    logger.info("[*] started listening for messages on %s", queue)
                    try:
                        await asyncio.Future()
                        logger.error("asyncio.Future() finished in ReceiveFromMythicDirectExchange for %s", queue)
                    except:
                        logger.exception("[-] exception trying to listen for direct messages on %s", queue)
            except aiormq.exceptions.ChannelLockedResource:
                logger.error("[-] Another instance of this service, %s, is running, failed to start, trying again...",
                             queue.split('_')[0])
                await asyncio.sleep(failedConnectRetryDelay)
            except:
                logger.exception("[-] stopped listening for messages on %s", queue)
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
                        callback=partial(rpcExchangeCallback, trueFunction=handler),
                    )
                    logger.info("[*] started listening for messages on %s", queue)
                    try:
                        await asyncio.Future()
                    finally:
                        logger.error("asyncio.Future() finished in ReceiveFromRPCQueue for queue %s", queue)
            except aiormq.exceptions.ChannelLockedResource:
                logger.error("[-] Another instance of this service, %s, is running, failed to start, trying again...", queue.split('_')[0])
                await asyncio.sleep(failedConnectRetryDelay)
            except:
                logger.exception("[-] stopped listening for messages on %s", queue)
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
                    logger.info("[*] started listening for messages on %s", queue)
                    try:
                        await asyncio.Future()
                        logger.error("asyncio.Future() finished in ReceiveFromMythicDirectTopicExchange for %s", queue)
                    except:
                        logger.exception(f"[-] exception trying to listen for direct messages on %s", queue)
            except:
                logger.exception("[-] stopped listening for messages on %s", queue)
                await asyncio.sleep(failedConnectRetryDelay)
