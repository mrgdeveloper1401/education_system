FROM docker.arvancloud.ir/nginx:1.29-alpine

COPY ./nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /var/www/static && \
    mkdir -p /etc/letsencrypt/live/codeima


ENTRYPOINT ["nginx", "-g", "daemon off;"]