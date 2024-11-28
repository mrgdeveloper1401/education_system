FROM python:3.12-alpine

WORKDIR /home/app

COPY . .

RUN apk update && \
    apk upgrade && \
    apk add python3 && \
    apk add py3-pip &&\
    apk add postgresql && \
    apk add nginx

RUN pip install --upgrade pip
RUN pip install -r /home/app/requirements/production.txt
RUN mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    adduser -D -H education && \
    chown -R 755 education
RUN python3 /home/app/manage.py collectstatic --settings=education_system.envs.production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDDONOTWRITEBYTECODE=1

ENTRYPOINT ["gunicorn", "education_system.wsgi", "-b"]
CMD ["0.0.0.0:8000"]
