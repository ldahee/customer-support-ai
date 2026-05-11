FROM python:3.11-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen
COPY . .
CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--host", "0.0.0.0"]
