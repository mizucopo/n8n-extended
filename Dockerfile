ARG N8N_VERSION=2.2.1
FROM n8nio/n8n:${N8N_VERSION}

RUN apt-get update && apt-get install -y docker-cli && apt-get clean
