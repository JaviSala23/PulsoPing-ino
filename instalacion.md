### 1. Preparativos iniciales

Asegúrate de que tu servidor Ubuntu esté configurado y actualizado. Instala Python, MySQL, y otras dependencias necesarias si aún no lo has hecho.

```bash
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3-dev mysql-server nginx
```

### 2. Configuración del entorno virtual (opcional pero recomendado)

Es buena práctica usar un entorno virtual para tu proyecto Django para mantener las dependencias separadas. Si aún no tienes `virtualenv`, instálalo:

```bash
sudo apt install virtualenv
```

Luego, crea y activa un entorno virtual para tu proyecto:

```bash
cd /home/PulsoPing-ino/api/apipulso
virtualenv venv
source venv/bin/activate
```

### 3. Instalación de dependencias del proyecto

Dentro del entorno virtual, instala las dependencias de tu proyecto Django, incluyendo `django`, `gunicorn`, `mysqlclient`, y `djangorestframework`:

```bash
pip install django gunicorn mysqlclient djangorestframework
```

### 4. Configuración de Django

Asegúrate de que tu configuración de Django (`settings.py`) esté ajustada para producción, incluyendo la configuración de la base de datos MySQL, configuraciones de seguridad como `DEBUG = False`, y configuración para `rest_framework`.

```python
# settings.py

INSTALLED_APPS = [
    ...
    'rest_framework',
    ...
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nombre_basedatos',
        'USER': 'nombre_usuario',
        'PASSWORD': 'contraseña',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

### 5. Configuración de MySQL

Crea una base de datos y un usuario para tu proyecto Django en MySQL:

```bash
mysql -u root -p
CREATE DATABASE nombre_basedatos;
CREATE USER 'nombre_usuario'@'localhost' IDENTIFIED BY 'contraseña';
GRANT ALL PRIVILEGES ON nombre_basedatos.* TO 'nombre_usuario'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. Configuración de nginx

Crea un archivo de configuración para tu proyecto Django en nginx. Crea un nuevo archivo de configuración en `/etc/nginx/sites-available/` (por ejemplo, `apipulso`) y configúralo para que nginx sirva tu aplicación Django a través de Gunicorn:

```nginx
server {
    listen 80;
    server_name tu_dominio_o_IP;

    location / {
        proxy_pass http://localhost:8000;  # Gunicorn escucha en el puerto 8000
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 1800;
        proxy_send_timeout 1800;
        proxy_read_timeout 1800;
        send_timeout 1800;
}
```

Activa el archivo de configuración de nginx creando un enlace simbólico en `sites-enabled`:

```bash
sudo ln -s /etc/nginx/sites-available/apipulso /etc/nginx/sites-enabled/
```

### 7. Configuración de Gunicorn

Crea un archivo de servicio para Gunicorn en `/etc/systemd/system/` (por ejemplo, `gunicorn.service`):

```ini
[Unit]
Description=Gunicorn daemon for Django Project
After=network.target

[Service]
User=usuario
Group=www-data
WorkingDirectory=/home/PulsoPing-ino/api/apipulso
ExecStart=/home/PulsoPing-ino/api/apipulso/venv/bin/gunicorn --workers 3 --bind unix:/home/PulsoPing-ino/api/apipulso/apipulso.sock apipulso.wsgi:application

[Install]
WantedBy=multi-user.target
```

Reemplaza `usuario` con tu nombre de usuario en el servidor.

### 8. Configuración final y reinicio de servicios

Guarda los cambios y reinicia nginx y Gunicorn para aplicar la configuración:

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl restart nginx
```

### 9. Configuración de Firewall (si es necesario)

Si estás utilizando un firewall, asegúrate de permitir el tráfico HTTP/HTTPS:

```bash
sudo ufw allow 'Nginx Full'
```

### 10. Verificación

Visita tu dominio o dirección IP en un navegador para verificar que tu aplicación Django se sirva correctamente a través de nginx.

Con estos pasos, tu proyecto Django debería estar configurado y funcionando en producción usando nginx como servidor web y MySQL como base de datos. Asegúrate de ajustar las configuraciones específicas según las necesidades exactas de tu aplicación.