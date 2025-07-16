FROM ultrafunk/undetected-chromedriver:latest
COPY --from=ghcr.io/astral-sh/uv:0.7.21-python3.11-alpine@sha256:8ad18d5d848621d6b08538e39d612e04e61d80bf497ea21d7f87825205f86531 /uv /uvx /bin/



ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1

RUN apt update && \
    apt install -y --no-install-recommends \
    build-essential \
    curl \
    cmake \
    gcc \
    git 
