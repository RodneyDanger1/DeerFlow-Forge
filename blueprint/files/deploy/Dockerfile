# Craft sandbox image. Build context is /opt/pod-pipeline.
# CLIs are the scripts in deploy/craft-bin until vendor binaries replace them.
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates imagemagick potrace ghostscript ffmpeg python3 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --uid 10001 --home-dir /tmp --shell /usr/sbin/nologin craft

COPY deploy/craft-bin/ /usr/local/bin/

USER 10001:10001
WORKDIR /tmp
