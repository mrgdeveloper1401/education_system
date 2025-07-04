FROM education:1.2.0

WORKDIR /home/app

COPY . .

RUN adduser -D -H mohammad && \
    chown -R mohammad:mohammad /home/app && \
    pip install -i https://mirror-pypi.runflare.com/simple httpx && \
    pip install -i https://mirror-pypi.runflare.com/simple psycopg_pool

USER mohammad

EXPOSE 800

#ENTRYPOINT ["sh", "-c", "/home/app/start.sh"]