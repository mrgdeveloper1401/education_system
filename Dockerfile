FROM python:3.12-alpine

WORKDIR /home/app

COPY . .

RUN apk update && \
    apk upgrade && \
    apk add python3 && \
    apk add py3-pip &&\
    apk add postgresql

RUN pip install --upgrade pip
RUN pip install -r /home/app/requirements/production.txt
RUN adduser -D -H mohammad
ENV DJANGO_SETTINGS_MODULE="education_system.envs.production"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDDONOTWRITEBYTECODE=1


ENTRYPOINT [ "gunicorn", "shop.wsgi", "-b"]
CMD ["0.0.0.0:8000"]
