FROM docker.arvancloud.ir/nginx:1.27-alpine

RUN mkdir /vol  && \
    mkdir -p /etc/letsencrypt/live/codeima.ir-0002 && \
    cp ./cert.pem /etc/letsencrypt/live/codeima.ir-0002 && \
    cp chain.pem /etc/letsencrypt/live/codeima.ir-0002 && \
    cp fullchain.pem /etc/letsencrypt/live/codeima.ir-0002 && \
    cp privkey.pem /etc/letsencrypt/live/codeima.ir-0002 && \
    cp README /etc/letsencrypt/live/codeima.ir-0002
