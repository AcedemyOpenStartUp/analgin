import traceback

from aio_pika.abc import AbstractIncomingMessage

from analgin.amqp.consumer import ConsumerBase


class FailedConsumer(ConsumerBase):
    def __init__(
        self,
        application_name,
        queue_name,
        connection,
        channel,
        exchange,
        prefetch_count=1,
    ):
        super().__init__(
            application_name, queue_name, connection, channel, exchange, prefetch_count
        )

    async def _on_message(self):
        while True:
            message: AbstractIncomingMessage = await self._internal_queue.get()
            try:
                await self.on_message(message)
                await message.ack()
            except Exception as e:
                await self._process_failed_message(message, e)

    async def _process_failed_message(
        self, message: AbstractIncomingMessage, reason: str
    ):
        error = traceback.format_exc()
        message.headers["failed-reason"] = error
        await self.exchange.publish(message, self._failed_queue.name)
        await message.ack()
        raise reason

    async def _setup_queues(self, args: dict | None = None):
        await super()._setup_queues(args)
        self._failed_queue = await self.channel.declare_queue(
            self._queue_name + "-failed", durable=True
        )
        await self._failed_queue.bind(self.exchange.name, self._failed_queue.name)
