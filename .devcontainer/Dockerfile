FROM ultrafunk/undetected-chromedriver:latest
COPY --from=ghcr.io/astral-sh/uv:0.7.21-python3.11-alpine /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1

RUN apt update && \
    apt install -y --no-install-recommends \
    build-essential \
    curl \
    cmake \
    gcc \
    git 
