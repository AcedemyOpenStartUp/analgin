from aio_pika.abc import AbstractChannel
from abc import ABC, abstractmethod

class Publisher(ABC):
    @abstractmethod
    async def publish(message: bytes, routing_key: str): ...