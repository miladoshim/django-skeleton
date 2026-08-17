import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = "%(asctime)s %(levelname)s %(message)s"
handler.setFormatter(logging.Formatter(formatter))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

critical_handler = logging.FileHandler("critical.log")
critical_handler.setLevel(logging.CRITICAL)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.threadName,
            "context": {
                "request_id": getattr(record, "request_id", None),
            },
        }
        if hasattr(record, "exc_info") and record.exc_info:
            import traceback

            log_record["stack_trace"] = "".join(
                traceback.format_exception(*record.exc_info)
            )

        return json.dumps(log_record)
