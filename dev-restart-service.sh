#!/bin/bash

sudo systemctl restart django-server.service
sudo systemctl restart nginx.service
sudo systemctl restart celery-service.service