import json
import logging
from datetime import datetime, timezone

from src.core.request_context import get_request_id


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "request_id": get_request_id(),
            "msg": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key.startswith("_"):
                continue
            if key in (
                    "msg", "args", "levelname", "levelno", "pathname",
                    "filename", "module", "exc_info", "exc_text",
                    "stack_info", "lineno", "funcName", "created",
                    "msecs", "relativeCreated", "thread", "threadName",
                    "processName", "process", "name"
            ):
                continue
            payload[key] = value

        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str = "app"):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


logger = get_logger()
