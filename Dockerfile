FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install uv
RUN uv sync

COPY src ./src
COPY . .

RUN chmod +x /app/startup.sh

ENTRYPOINT ["/app/startup.sh"]