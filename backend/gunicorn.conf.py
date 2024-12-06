# Number of worker processes
workers = 3

# The socket to bind
bind = "0.0.0.0:8000"

# Timeout for worker processes
timeout = 120

# Maximum number of pending connections
backlog = 2048

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'