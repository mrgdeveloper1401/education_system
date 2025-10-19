FROM education:2.0.0

WORKDIR /home/app

COPY . .

# RUN adduser -D -H mohammad && \
#     chown -R mohammad:mohammad /home/app
RUN chmod +x /home/app/start.sh

# USER mohammad

EXPOSE 800

ENTRYPOINT ["bash", "/home/app/start.sh"]