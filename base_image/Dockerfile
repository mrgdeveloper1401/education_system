FROM docker.arvancloud.ir/python:3.12.10-alpine

COPY requirements.txt .

RUN cp /dev/null /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/main" >> /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/community" >> /etc/apk/repositories && \
    apk update && \
    apk upgrade && \
    apk add --no-cache bash gcc postgresql16-client vim && \
    pip install --index-url https://mirror-pypi.runflare.com/simple -r requirements.txt