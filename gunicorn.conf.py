import os

bind = "0.0.0.0:" + os.environ.get("PORT", "8001")
# Keep local development within a modest process budget. Hosting platforms can
# set WEB_CONCURRENCY explicitly after sizing the instance and Redis pool.
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "gthread"
threads = 4
timeout = 90
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
