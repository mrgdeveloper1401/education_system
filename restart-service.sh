#!/bin/bash

sudo systemctl restart django-server.service
sudo systemctl restart nginx.service
sudo systemctl status celery-service.service