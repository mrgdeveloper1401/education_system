#!/bin/bash

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
gunicorn core.asgi:application -k uvicorn_worker.UvicornWorker -w 3 -b 0.0.0.0:8000