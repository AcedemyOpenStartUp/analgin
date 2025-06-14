import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Optional

from analgin.log.abc import Logger


class StructuredLogger(Logger):
    """Structured logger that outputs JSON formatted logs."""

    def __init__(
        self,
        service_name: str,
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        when: str = "D",
        interval: int = 1,
        backup_count: int = 30,
    ):
        """
        Initialize the structured logger.

        Args:
            service_name: Name of the service using this logger
            level: Logging level
            log_file: Optional file to write logs to
            when: Interval type for TimedRotatingFileHandler (S, M, H, D)
            interval: Interval for rotating logs
            backup_count: Number of backup files to keep
        """
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(level)

        # JSON formatter
        formatter = logging.Formatter("%(message)s")

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler if log_file is specified
        if log_file:
            file_handler = TimedRotatingFileHandler(
                filename=log_file,
                when=when,
                interval=interval,
                backupCount=backup_count,
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _format_log(self, level: str, message: str, **kwargs: Any) -> str:
        """Format log entry as JSON string."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            **kwargs,
        }
        return json.dumps(log_entry)

    async def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(self._format_log("INFO", message, **kwargs))

    async def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(self._format_log("ERROR", message, **kwargs))

    async def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(self._format_log("WARNING", message, **kwargs))

    async def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(self._format_log("DEBUG", message, **kwargs))

    async def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.logger.critical(self._format_log("CRITICAL", message, **kwargs))
