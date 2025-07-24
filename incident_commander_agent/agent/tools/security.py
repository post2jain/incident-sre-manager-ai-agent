from __future__ import annotations
import os, re
from fastapi import Header, HTTPException

API_KEY = os.getenv("MCP_API_KEY", "").strip()

def verify_api_key(x_api_key: str | None = Header(default=None)):
    if not API_KEY:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

PROMQL_ALLOWED = re.compile(r"^[a-zA-Z_:][a-zA-Z0-9_:]*$")

def validate_promql(promql: str):
    metric = promql.split("(")[-1].split(")")[0].split("{")[0].strip().strip("}")
    if not PROMQL_ALLOWED.match(metric):
        raise HTTPException(status_code=400, detail="Disallowed promql metric name")
    return promql
