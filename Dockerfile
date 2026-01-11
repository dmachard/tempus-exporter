FROM python:3.14-alpine

LABEL name="Tempus Exporter"

WORKDIR /app

COPY requirements.txt .
RUN apk add --no-cache \
    tzdata \
    build-base \
    python3-dev \
    libffi-dev \
    openssl-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apk del build-base python3-dev
 
COPY tempus ./tempus

RUN adduser -D tempus && chown -R tempus:tempus /app
USER tempus

EXPOSE 8000

ENTRYPOINT ["python", "-m", "tempus"]