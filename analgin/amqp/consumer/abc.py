from abc import ABC, abstractmethod

from aio_pika.abc import AbstractConnection, AbstractIncomingMessage, AbstractQueue


class Consumer(ABC):
    @property
    @abstractmethod
    def connection(self) -> AbstractConnection:
        raise NotImplementedError

    @property
    @abstractmethod
    def queue(self) -> AbstractQueue:
        raise NotImplementedError

    @abstractmethod
    async def run(self):
        raise NotImplementedError

    @abstractmethod
    async def _on_message(self):
        raise NotImplementedError

    @abstractmethod
    async def on_message(self, message: AbstractIncomingMessage):
        raise NotImplementedError

    @abstractmethod
    async def _start_consuming(self):
        raise NotImplementedError
