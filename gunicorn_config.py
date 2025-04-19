import os

port = os.getenv('PORT', '10000')
bind = f"0.0.0.0:{port}"
workers = 1  # Reduced from 4 to stay within memory limits
threads = 2
timeout = 120
keepalive = 5
worker_class = 'gthread'
max_requests = 1000
max_requests_jitter = 50
preload_app = True 