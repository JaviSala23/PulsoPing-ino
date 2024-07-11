import multiprocessing

# Nombre del módulo WSGI de tu proyecto Django
bind = 'unix:/home/PulsoPing-ino/api/apipulso/PulsoPing-ino.sock'
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 30