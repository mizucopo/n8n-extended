ARG N8N_VERSION=2.2.1

FROM alpine:3.19 AS docker-cli
RUN apk add --no-cache curl && \
    curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.3.1.tgz -o docker.tgz && \
    tar xzvf docker.tgz && \
    rm docker.tgz

FROM n8nio/n8n:${N8N_VERSION}
USER root
COPY --from=docker-cli docker/docker /usr/local/bin/docker
RUN chmod +x /usr/local/bin/docker

USER node
