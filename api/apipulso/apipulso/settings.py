"""
Django settings for apipulso project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-xgqe#1rn!-*8xug4$)r1nd@z5#$1ka%p=75)#7oq&c**e05m9('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['habitatonline.ar']




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'pulso',
    'gestion'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'apipulso.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries':{
            'auth_extras': 'templatetags.auth_extras',
            
            }
        },
    },  
]

WSGI_APPLICATION = 'apipulso.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {
    'default': { 
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'sensor',
        'USER': 'root',
        'PASSWORD': 'Celeste14',
        'HOST': 'localhost',
        'PORT': '3306'
        }
    
}

    
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es-ar'  # Cambia el idioma a español (Argentina)

TIME_ZONE = 'America/Argentina/Buenos_Aires'  # Establece la zona horaria a Buenos Aires
USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
os.path.join(BASE_DIR, "static")
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#expiracion de sesion
#SESSION_COOKIE_AGE = 3600 # 600 segundos = 10 minutos
#SESSION_EXPIRE_AT_BROWSER_CLOSE = False


EMAIL_USE_TLS=True
EMAIL_HOST ='mail.mantistec.com.ar'
EMAIL_PORT=22
EMAIL_HOST_USER='info@mantistec.com.ar'
EMAIL_HOST_PASSWORD='jXGH%*C{c_8='
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'


CORS_ORIGIN_ALLOW_ALL = True  # Permite que cualquier origen acceda a tu servidor (solo para pruebas, NO recomendado para producción)
CORS_ALLOW_CREDENTIALS = True  # Permite enviar credenciales (por ejemplo, cookies) en solicitudes CORS
CORS_ALLOWED_ORIGINS = [
    
    # Lista de orígenes permitidos (por ejemplo, 'http://localhost:8000', 'http://habitatonline.ar', etc.)
    # Asegúrate de agregar los orígenes desde donde se realizarán las solicitudes (por ejemplo, el servidor PHP)
]
CORS_ALLOWED_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]  # Métodos HTTP permitidos en solicitudes CORS
CORS_ALLOWED_HEADERS = [
    'Accept',
    'Accept-Encoding',
    'Authorization',
    'Content-Type',
    'DNT',
    'Origin',
    'User-Agent',
    'X-CSRFToken',
    'X-Requested-With',
    
]  # Encabezados permitidos en solicitudes CORS

