FROM docker.arvancloud.ir/nginx:1.27-alpine

COPY ./nginx.conf /etc/nginx/nginx.conf

RUN mkdir /vol && \
    mkdir -p /etc/letsencrypt/live/codeima

COPY ./codeima /etc/letsencrypt/live/codeima

RUN chmod +x -R /etc/letsencrypt/live/codeima