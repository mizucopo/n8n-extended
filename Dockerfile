ARG N8N_VERSION
ARG ALPINE_VERSION=3.24
ARG DOCKER_VERSION=29.2.1

# Stage 1: Download Docker CLI
FROM alpine:${ALPINE_VERSION} AS tools
ARG DOCKER_VERSION
RUN apk add --no-cache curl apk-tools-static && \
    curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz -o docker.tgz && \
    tar xzf docker.tgz && \
    rm docker.tgz

# Stage 2: Build final image
FROM n8nio/n8n:${N8N_VERSION}
USER root
WORKDIR /root
ARG ALPINE_VERSION

# Copy Docker CLI
COPY --from=tools docker/docker /usr/local/bin/docker

# Copy static apk and install ffmpeg
COPY --from=tools /sbin/apk.static /sbin/apk
RUN chmod +x /usr/local/bin/docker && \
    chmod +x /sbin/apk && \
    echo "https://dl-cdn.alpinelinux.org/alpine/v${ALPINE_VERSION}/main" > /etc/apk/repositories && \
    echo "https://dl-cdn.alpinelinux.org/alpine/v${ALPINE_VERSION}/community" >> /etc/apk/repositories && \
    /sbin/apk add --no-cache ffmpeg && \
    rm -rf /var/cache/apk/*
