FROM n8nio/n8n:2.2.1

RUN apt-get update && apt-get install -y docker-cli && apt-get clean
