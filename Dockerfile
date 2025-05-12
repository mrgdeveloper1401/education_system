FROM education:1.0.0

WORKDIR /home/app

COPY . .

RUN adduser -D -H mohammad && \
    chown -R mohammad:mohammad /home/app && \
    pip install --index-url https://mirror-pypi.runflare.com/simple/ psycopg2-binary

USER mohammad

ENTRYPOINT ["sh", "-c", "/home/app/start.sh"]