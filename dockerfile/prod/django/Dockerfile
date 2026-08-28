FROM education:1.0.0

WORKDIR /home/app

COPY . .

RUN chmod +x /home/app/scripts/start.sh

EXPOSE 8000

# CMD /bin/bash
ENTRYPOINT ["/home/app/scripts/start.sh"]
