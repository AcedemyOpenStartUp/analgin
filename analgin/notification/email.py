from aio_pika.abc import AbstractExchange
from aio_pika import Message
import json


class EmailNotification:
    def __init__(
        self, exchange: AbstractExchange, routing_key: str
    ):
        self._exchange = exchange
        self._routing_key = routing_key

    async def send(
        self,
        email_from: str,
        email_to: str,
        subject: str,
        type: str,
        context: dict = {},
    ):
        data = {
            "from": email_from,
            "to": email_to,
            "subject": subject,
            "template": type,
            "context": context,
        }
        message = Message(body=json.dumps(data).encode())
        await self._exchange.publish(message=message, routing_key=self._routing_key)
