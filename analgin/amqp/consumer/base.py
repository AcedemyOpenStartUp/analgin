import asyncio
import datetime
import socket
from abc import abstractmethod
from datetime import timezone

from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
)

from analgin.amqp.consumer.abc import Consumer


class ConsumerBase(Consumer):
    def __init__(
        self,
        application_name: str,
        queue_name: str,
        connection: AbstractConnection,
        channel: AbstractChannel,
        exchange: AbstractExchange,
        prefetch_count: int = 1,
    ):
        self.__application_name = application_name
        self._queue_name = queue_name
        self.__prefetch_count = prefetch_count
        self.__connection = connection
        self.__channel = channel
        self.__exchange = exchange

        self._internal_queue = asyncio.Queue()

    @property
    def exchange(self) -> AbstractExchange:
        return self.__exchange

    @property
    def queue(self) -> AbstractQueue:
        return self.__queue

    @property
    def connection(self) -> AbstractConnection:
        return self.__connection

    @property
    def channel(self) -> AbstractChannel:
        return self.__channel

    @property
    def arguments(self):
        return {
            "ex-consumer-info": {
                "host": socket.gethostname(),
                "start_time": str(datetime.datetime.now(timezone.utc)),
            }
        }

    async def run(self):
        await self._setup_queues()
        await self._start_consuming()

    async def _on_message(self):
        while True:
            message: AbstractIncomingMessage = await self._internal_queue.get()
            await self.on_message(message)
            await message.ack()

    @abstractmethod
    async def on_message(self, message: AbstractIncomingMessage):
        raise NotImplementedError

    async def _start_consuming(self):
        await self.queue.channel.set_qos(self.__prefetch_count)
        await self.queue.consume(
            callback=self._internal_queue.put,
            arguments=self.arguments,
            consumer_tag=self.__application_name,
        )

        workers = [
            asyncio.create_task(self._on_message())
            for _ in range(self.__prefetch_count)
        ]

        await asyncio.gather(*workers)

    async def _setup_queues(self, args: dict | None = None):
        self.__queue = await self.__channel.declare_queue(
            self._queue_name, durable=True, arguments=args
        )
        await self.__queue.bind(self.exchange, self.__queue.name)

    async def close(self):
        await self.__channel.close()
        await self.__connection.close()
