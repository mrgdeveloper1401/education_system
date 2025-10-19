FROM education:2.0.0

WORKDIR /home/app

COPY . .

# RUN adduser -D -H mohammad && \
#     chown -R mohammad:mohammad /home/app
RUN chmod +x /home/app/start.sh && \
    pip install --index-url https://mirror-pypi.runflare.com/simple gunicorn && \ 
    pip install --index-url https://mirror-pypi.runflare.com/simple corsheaders

# USER mohammad

EXPOSE 8000

# CMD /bin/bash
ENTRYPOINT ["/home/app/start.sh"]
