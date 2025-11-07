FROM docker.arvancloud.ir/nginx:1.27.5-alpine

COPY ./nginx.conf /etc/nginx/nginx.conf

RUN mkdir /vol && \
    mkdir -p /etc/letsencrypt/live/codeima && \
    mkdir -p /var/www/mobile_static

COPY ./codeima /etc/letsencrypt/live/codeima
