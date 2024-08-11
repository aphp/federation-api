ARG IMAGE_FROM="python:3.12.5-slim"
FROM ${IMAGE_FROM} AS builder
WORKDIR /app

ENV VIRTUAL_ENV=/app/venv
RUN apt-get update -y && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt .
RUN pip install uv && uv venv $VIRTUAL_ENV && uv pip install --no-cache -r requirements.txt

FROM ${IMAGE_FROM} AS final
WORKDIR /app

ENV VIRTUAL_ENV=/app/venv \
    PATH="$VIRTUAL_ENV/bin:$PATH" \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
    && apt-get install -y curl nano cron \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
COPY . .

EXPOSE 8000
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]
