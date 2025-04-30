FROM python:3.12-alpine

WORKDIR /home/app

COPY . .

RUN apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add --no-cache postgresql

RUN pip install --upgrade pip && \
    pip install -r requirements/production.txt && \
    adduser -D -H mohammad && \
    chown -R mohammad:mohammad /home/app && \
    chmod +x /home/app/start.sh

USER mohammad

ENTRYPOINT ["sh", "-c", "/home/app/start.sh"]