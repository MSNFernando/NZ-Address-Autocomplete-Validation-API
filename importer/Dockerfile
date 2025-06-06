FROM alpine:3.18

RUN apk add --no-cache curl postgresql-client

WORKDIR /app

COPY import_addresses.sh .
RUN chmod +x import_addresses.sh
