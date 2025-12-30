import logging
import sys
from typing import Optional

from app.core.config import get_settings

settings = get_settings()


# -------------------------------------------------
# Log Formatters
# -------------------------------------------------
class JsonFormatter(logging.Formatter):
    """
    Outputs logs in structured JSON format.
    Suitable for log aggregation systems (ELK, CloudWatch, Datadog).
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Optional structured fields
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id

        if hasattr(record, "path"):
            log_record["path"] = record.path

        if hasattr(record, "method"):
            log_record["method"] = record.method

        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code

        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return str(log_record)


# -------------------------------------------------
# Logging Setup
# -------------------------------------------------
def setup_logging() -> None:
    """
    Configures application-wide logging.

    - JSON logs in production
    - Human-readable logs in development
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Clear existing handlers (important for reloads)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if settings.APP_ENV == "production":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
            )
        )

    root_logger.addHandler(handler)


# -------------------------------------------------
# Logger Factory
# -------------------------------------------------
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Returns a configured logger instance.
    """
    return logging.getLogger(name)
