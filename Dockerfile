FROM python:3.12-alpine

WORKDIR /home/app

COPY . .

RUN apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add py3-pip

RUN pip install --upgrade pip && \
    pip install -r requirements/production.txt && \
    adduser -D -H mohammad && \
    chown -R mohammad:mohammad /home/app


USER mohammad

ENTRYPOINT ["sh", "-c", "/home/app/start.sh"]