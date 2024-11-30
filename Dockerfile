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

RUN chmod +x /home/app/manage.py

ENV PYTHONUNBUFFERED=1
ENV PYTHONDDONOTWRITEBYTECODE=1

RUN python3 /home/app/manage.py collectstatic --noinput

ENTRYPOINT ["gunicorn", "education_system.wsgi", "-b"]
CMD ["0.0.0.0:8000"]
