FROM ultrafunk/undetected-chromedriver:latest
COPY --from=ghcr.io/astral-sh/uv:0.7.21@sha256:4b4fb0254be5909c4687e23a32d0e60e2bf315fe0d4a10e10c7b941f45a5b60c /uv /uvx /bin/



ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1

RUN apt update && \
    apt install -y --no-install-recommends \
    build-essential \
    curl \
    cmake \
    gcc \
    git 
