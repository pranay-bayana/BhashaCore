bind = "0.0.0.0:" + __import__("os").environ.get("PORT", "8001")
workers = __import__("os").cpu_count() or 2
worker_class = "gthread"
threads = 4
timeout = 90
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
