FROM python:3.12-alpine

WORKDIR /home/app

COPY . .

RUN apk update && \
    apk upgrade && \
    apk add py3-pip


RUN pip install -r /home/app/requirements/production.txt
