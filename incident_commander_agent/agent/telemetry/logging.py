import json, time
from typing import Any, Dict

def log_event(event_type: str, **kwargs: Any):
    payload: Dict[str, Any] = {"ts": time.time(), "event": event_type, **kwargs}
    print(json.dumps(payload, ensure_ascii=False))
