ARG N8N_VERSION=2.2.1
FROM n8nio/n8n:${N8N_VERSION}

RUN apk add --no-cache docker
