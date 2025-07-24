FROM python:3.11-slim AS base
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ['uvicorn', 'agent.tools.mcp_api:app', '--host', '0.0.0.0', '--port', '8000']
