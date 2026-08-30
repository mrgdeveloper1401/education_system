# gunicorn.conf.py version 26
import multiprocessing

bind = "0.0.0.0:8000"  # host
workers = multiprocessing.cpu_count() * 2 + 1  # max worker number
# worker_class = "uvicorn.workers.UvicornWorker"  # worker type
worker_class = "gthread"  # worker type
if worker_class == "gthread":
    threads = 4  # for 1 core --> 4 * 5 = 20 (request concurrency)
worker_connections = 1000  # max connection management per worker
max_requests = 1000  # restart worker when process 10000 requests
max_requests_jitter = 200
keepalive = 5  # max time open connection between backend and nginx
timeout = 30  # Maximum processing time for a request
graceful_timeout = 30  # max timeworker shutdown
reuse_port = True
preload_app = True

# Logging
loglevel = "debug"
errorlog = "-"
accesslog = "-"  # چاپ لاگ درخواست‌های ورودی در کنسول داکر
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s µs'
capture_output = True  # گرفتن خروجی‌های استاندارد پایتون (stdout/stderr)

def post_fork(server, worker):
    from django.db.backends.postgresql.base import DatabaseWrapper

    # clear connection pool where preload_app equal true and inheritance worker
    DatabaseWrapper._connection_pools.clear()
