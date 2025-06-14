from abc import ABC, abstractmethod
from typing import Any


class Logger(ABC):
    """Abstract base class for logging."""

    @abstractmethod
    async def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with context."""
        pass

    @abstractmethod
    async def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with context."""
        pass

    @abstractmethod
    async def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with context."""
        pass

    @abstractmethod
    async def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with context."""
        pass

    @abstractmethod
    async def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with context."""
        pass
