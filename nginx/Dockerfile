FROM docker.arvancloud.ir/nginx:1.27-alpine

COPY ./nginx.conf /etc/nginx/nginx.conf

RUN mkdir /vol && \
    mkdir -p /etc/letsencrypt/live/codeima && \
    COPY ./nginx.conf /etc/nginx/nginx.conf && \
    COPY ./codeima /etc/letsencrypt/live/codeima