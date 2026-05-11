#!/bin/sh
exec /app/.venv/bin/uvicorn mcp_servers.slack_notify.server:asgi_app --host 0.0.0.0 --port "${PORT:-8011}"
