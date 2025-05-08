from analgin.amqp.publisher.abc import Publisher
from aio_pika.abc import AbstractExchange, AbstractConnection
from aio_pika import Message


class PublisherBase(Publisher):
    def __init__(self, conn: AbstractConnection, exchange: AbstractExchange):
        self._conn = conn
        self._exchange = exchange

    async def publish(
        self,
        message: bytes,
        routing_key: str,
        headers: dict = {},
        content_type: str = "application/json",
    ):
        message = Message(body=message, headers=headers, content_type=content_type)
        await self._exchange.publish(message, routing_key=routing_key)
