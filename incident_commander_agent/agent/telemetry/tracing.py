from contextlib import contextmanager
import time
from agent.telemetry.logging import log_event

@contextmanager
def span(name: str, **attrs):
    start = time.time()
    log_event("span_start", name=name, **attrs)
    try:
        yield
    finally:
        dur = time.time() - start
        log_event("span_end", name=name, duration_s=dur)
