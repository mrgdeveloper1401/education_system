# ==========================================
# مرحله 1: نصب و build وابستگی‌های پایتون
# ==========================================
FROM docker.arvancloud.ir/python:3.14-alpine AS builder

WORKDIR /build

COPY requirements.txt .

RUN cp /dev/null /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/main" >> /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/community" >> /etc/apk/repositories && \
    apk add --no-cache \
        build-base \
        linux-headers \
        libpq-dev && \
    python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install \
        --no-cache-dir \
        --index-url https://mirror-pypi.runflare.com/simple \
        -r requirements.txt


# ==========================================
# مرحله 2: image نهایی و سبک‌تر برای اجرا
# ==========================================
FROM docker.arvancloud.ir/python:3.14-alpine

WORKDIR /home/app

RUN cp /dev/null /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/main" >> /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/community" >> /etc/apk/repositories && \
    apk add --no-cache \
        libpq \
        jpeg \
        zlib \
        freetype \
        bash

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
