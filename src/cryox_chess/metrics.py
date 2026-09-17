from __future__ import annotations

import time
from pathlib import Path

from .io import append_jsonl


class MetricsWriter:
    def __init__(self, path: Path) -> None:
        self.path = path

    def write(self, event: str, **values: object) -> None:
        append_jsonl(
            self.path,
            {
                "timestamp": time.time(),
                "event": event,
                **values,
            },
        )
