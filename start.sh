#!/bin/bash

python /home/app/manage.py collectstatic --noinput
python /home/app/manage.py makemigrations
python /home/app/manage.py migrate
gunicorn /home/app/education_system.wsgi -w 4 -b 0.0.0.0:8000