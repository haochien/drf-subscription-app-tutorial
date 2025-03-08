import multiprocessing

# Workers and threads configuration
cpu_count = multiprocessing.cpu_count()
workers = cpu_count * 2 + 1
threads = cpu_count * 2  # 2 threads per core is a good starting point

# The socket to bind
bind = "0.0.0.0:8000"

# Worker class configuration
worker_class = "gthread"  # Use threaded worker

# Performance tuning
worker_tmp_dir = "/dev/shm"  # Use memory for temp files to improve performance

# Process management
timeout = 120  # Timeout for worker processes
graceful_timeout = 30  # Time to finish serving requests before restart
max_requests = 1000    # Restart workers after this many requests
max_requests_jitter = 50  # Add randomness to avoid all workers restarting together

# Connection settings
backlog = 2048  # Maximum number of pending connections
keepalive = 5  # Keep connections open for 5 seconds

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

