ARG base_image="debian:bookworm-slim"
FROM ghcr.io/astral-sh/uv:0.7.11 AS uv

# ------------------------
FROM ${base_image} AS development

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:/app/.venv/bin:$PATH" \
    UV_LINK_MODE="copy"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates make git curl ssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /bin/

# Setup UV with autocompletion
RUN uv generate-shell-completion bash > ~/.uv_bash_completion \
    && echo "source $HOME/.uv_bash_completion" >> ~/.bashrc

# Note: Python is installed by UV, based on .python-version declaration
COPY .python-version pyproject.toml uv.lock /app/
COPY bootstrap/ /app/bootstrap/
COPY adapters/ /app/adapters/
COPY domain/ /app/domain/
COPY tests/ /app/tests/
COPY application/ /app/application/
RUN uv sync \
    --directory /app \
    --frozen \
    --no-install-project

CMD [ "/bin/sh", "-c", "uvicorn bootstrap.web_app:bootstrap_web_api --host 0.0.0.0 --port $PORT --reload --factory" ]

VOLUME [ "/app/.venv" ]

# ------------------------
FROM ${base_image} AS production-builder-base

COPY --from=uv /uv /uvx /bin/

# Note: Python is installed by UV, based on .python-version declaration
COPY .python-version pyproject.toml uv.lock /app/
COPY bootstrap/ /app/bootstrap/
COPY adapters/ /app/adapters/
COPY domain/ /app/domain/
COPY tests/ /app/tests/
COPY application/ /app/application/
RUN uv sync \
    --directory /app \
    --frozen \
    --compile-bytecode \
    --no-install-project \
    --no-editable \
    --no-dev

# ------------------------
FROM ${base_image} AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Python UV installation and created virtual environment
COPY --from=production-builder-base /root/.local /root/.local
COPY --from=production-builder-base /app/.venv /app/.venv

WORKDIR /app
COPY . ./

# Run app in single process, to allow better scaling at infrastructure level:
# https://fastapi.tiangolo.com/deployment/docker/
CMD [ "sh", "-c", "uvicorn bootstrap.web_app:bootstrap_web_api --host 0.0.0.0 --port $PORT --factory" ]
