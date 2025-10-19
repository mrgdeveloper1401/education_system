FROM education:2.0.0

WORKDIR /home/app

COPY . .

# RUN adduser -D -H mohammad && \
#     chown -R mohammad:mohammad /home/app


USER mohammad

EXPOSE 800

#ENTRYPOINT ["sh", "-c", "/home/app/start.sh"]