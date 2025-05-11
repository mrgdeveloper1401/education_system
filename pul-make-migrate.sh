#!/bin/bash

PATH="/home/debian/django_project/education_system/.venv/bin"

git pull

python manage.py makemigrations

python manage.py migrate