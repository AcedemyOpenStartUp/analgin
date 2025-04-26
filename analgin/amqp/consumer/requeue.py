import traceback

from aio_pika.abc import AbstractIncomingMessage

from analgin.amqp.consumer import FailedConsumer


class RequeueConsumer(FailedConsumer):
    def __init__(
        self,
        application_name,
        queue_name,
        connection,
        channel,
        exchange,
        retry_count: int,
        retry_sec: int,
        prefetch_count=1,
    ):
        super().__init__(
            application_name, queue_name, connection, channel, exchange, prefetch_count
        )

        self._retry_count = retry_count
        self._retry_sec = retry_sec

    async def _process_failed_message(self, message, reason):
        if self.can_retry(message):
            await message.nack(requeue=False)
        else:
            error = traceback.format_exc()
            message.headers["failed-reason"] = error
            await self.exchange.publish(message, self._failed_queue.name)
            await message.ack()
            raise reason

    def can_retry(self, message: AbstractIncomingMessage):
        deaths = (message.properties.headers or {}).get("x-death")
        if not deaths:
            return True
        return not deaths[0]["count"] >= self._retry_count

    async def _setup_queues(self):
        await super()._setup_queues(
            args={
                "x-dead-letter-exchange": self.exchange.name,
                "x-dead-letter-routing-key": self._queue_name + "-delay",
            }
        )
        self._delay_queue = await self.channel.declare_queue(
            self._queue_name + "-delay",
            durable=True,
            arguments={
                "x-message-ttl": self._retry_sec * 1000,
                "x-dead-letter-exchange": self.exchange.name,
                "x-dead-letter-routing-key": self._queue_name,
            },
        )
        await self._delay_queue.bind(self.exchange.name, self._delay_queue.name)
