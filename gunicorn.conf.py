import multiprocessing
import os

# Server socket
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'flowrite'
pythonpath = '.'

# Logging
accesslog = 'logs/gunicorn.access.log'
errorlog = 'logs/gunicorn.error.log'
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# Process management
daemon = False
pidfile = 'gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Server mechanics
preload_app = True
reload = False  # Set to True for development
spew = False
check_config = False

# Server hooks
def on_starting(server):
    """Log that Gunicorn is starting."""
    server.log.info("Starting Gunicorn server...")

def on_exit(server):
    """Clean up on shutdown.""" 