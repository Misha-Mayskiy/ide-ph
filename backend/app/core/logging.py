import json
import logging
from datetime import UTC, datetime


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


logger = logging.getLogger("ide_builder")


def log_event(event: str, **fields: object) -> None:
    payload = {
        "ts": datetime.now(UTC).isoformat(),
        "event": event,
        **fields,
    }
    logger.info(json.dumps(payload, ensure_ascii=False))
