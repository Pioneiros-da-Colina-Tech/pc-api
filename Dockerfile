FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:{PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv python install 3.13
RUN uv sync --python 3.13 --frozen --no-dev

COPY app ./app

FROM debian:bookworm-slim AS runtime

ENV PATH="/app/.venv/bin:${PATH}"
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app ./app

EXPOSE 8000

CMD [ "uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]