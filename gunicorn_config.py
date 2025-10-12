# Gunicorn configuration file for Render.com deployment
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
backlog = 2048

# Worker processes - Optimized for Render $7/month plan (512MB RAM)
# Use 4 workers for better performance while staying within memory limits
workers = int(os.getenv('WEB_CONCURRENCY', 4))
worker_class = 'sync'
worker_connections = 500  # Balanced for 4 workers
max_requests = 500  # Restart workers after 500 requests to prevent memory leaks
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Memory optimization
worker_tmp_dir = '/dev/shm'  # Use RAM disk for temporary files

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'goalpredictor_ai'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (handled by Render)
keyfile = None
certfile = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Application
wsgi_app = 'app:app'
reload = False  # Don't use in production
preload_app = True

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 GoalPredictor.AI starting on Render.com...")

def on_reload(server):
    """Called to recycle workers during a reload."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    print("✅ Server is ready. Waiting for requests...")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"👷 Worker spawned (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    print("Forking new master process...")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    print(f"⚠️ Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    print(f"❌ Worker aborted (pid: {worker.pid})")
