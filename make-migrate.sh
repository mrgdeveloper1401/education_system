#!/bin/bash

PATH="/home/debian/django_project/education_system/.venv/bin"

python manage.py makemigrations

python manage.py migrate