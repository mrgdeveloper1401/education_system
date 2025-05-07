#!/bin/bash

sudo systemctl restart gunicorn-service.service
sudo systemctl restart nginx.service
sudo systemctl restart celery-service.service