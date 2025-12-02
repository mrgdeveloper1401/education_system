FROM education:1.0.0

WORKDIR /home/app

COPY . .

# RUN adduser -D -H mohammad && \
#     chown -R mohammad:mohammad /home/app
RUN chmod +x /home/app/dockerfile/prod/django/start.sh

# USER mohammad

EXPOSE 8000

# CMD /bin/bash
ENTRYPOINT ["/home/app/start.sh"]
