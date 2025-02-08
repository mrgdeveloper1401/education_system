FROM python:3.12-alpine

WORKDIR /home/app

RUN apk update && \
    apk add --no-cache gcc musl-dev libpq postgresql-dev

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements/production.txt

RUN adduser -D -H mohammad && \
    mkdir -p /vol/media && \
    mkdir -p /vol/static && \
    chown -R mohammad:mohammad /vol && \
    chown -R mohammad:mohammad /home/app && \
    chmod +x ./start.sh

USER mohammad

ENTRYPOINT ["sh", "-c", "/home/app/start.sh"]
