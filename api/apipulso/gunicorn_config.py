import multiprocessing

# Nombre del módulo WSGI de tu proyecto Django
bind = 'unix:/path/to/your/django/project/yourproject.sock'
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 30