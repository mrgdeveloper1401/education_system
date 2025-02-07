FROM python:3.12-alpine

WORKDIR /home/app

COPY . .

RUN apk update && \
    apk upgrade && \
    apk add python3 && \
    apk add py3-pip && \
    apk add postgresql && \
    apk add nginx && \
    apk add celery

RUN pip install --upgrade pip
RUN pip install -r /home/app/requirements/production.txt

RUN adduser -D -H mohammad && \
    chown -R mohammad:mohammad /home/app && \
    chmod +x /home/app/start.sh

ENTRYPOINT ["sh", "-c", "./start.sh"]