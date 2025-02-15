#!/bin/sh

NAME="education_system"
DJANGODIR="/home/app"
SOCKFILE=""
USER=education_system
GROUP=education_system
NUM_WORKERS=1
DJANGO_SETTINGS_MODULE="/home/app/education_system.envs.production"
DJANGO_WSGI_MODULE="/home/app/education_system.wsgi"
TIMEOUT=120

cd $DJANGODIR
#source active environment, if you have need
export DJANGO_WSGI_MODULE=$DJANGO_WSGI_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

RUNDIR=$(dirname $SOCKFILE)

exec ../bin/gunicorn ${DJANGO_WSGI_MODULE}:applocation \
--name $NAME \
--workers $NUM_WORKERS \
--timeout $TIMEOUT \
--user=$USER --group=$GROUP \
--bind-unix:$SOCKFILE \
--log-level-debug \
--log-file=-