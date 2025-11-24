"""
© Ocado Group
Created on 20/11/2025 at 13:33:20(+00:00).
"""

import json
import logging
import sys
import typing as t
from contextvars import ContextVar
from datetime import datetime, timezone

LOG_CONTEXT: ContextVar[t.Dict[str, t.Any]] = ContextVar(
    "log_context", default={}
)


class JsonFormatter(logging.Formatter):
    """
    Formats log records as a JSON string.
    Automatically injects metadata from the LOG_CONTEXT ContextVar.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "time": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "logger": record.name,
            "location": f"{record.module}:{record.funcName}:{record.lineno}",
        }

        # Merge in the request-specific metadata (bucket, blob, event_id)
        context = LOG_CONTEXT.get()
        log_obj.update(context)

        # Add any extra props (e.g. extra={"foo": "bar"}) passed in the log call
        if hasattr(record, "props"):
            log_obj.update(record.props)

        return json.dumps(log_obj)


# Configure the root logger once
root_logger = logging.getLogger()
for handler in root_logger.handlers.copy():
    root_logger.removeHandler(handler)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)
