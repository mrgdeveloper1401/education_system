FROM mrgdocker2023/dj_5_base

WORKDIR /home/app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r /home/app/requirements/production.txt

RUN adduser -D -H mohammad && \
    chown -R mohammad:mohammad /home/app && \
    chmod +x /home/app/start.sh

ENTRYPOINT ["sh", "-c", "./start.sh"]