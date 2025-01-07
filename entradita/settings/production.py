# entradita/settings/production.py

from .base import *
import dj_database_url
from dotenv import load_dotenv
import os

load_dotenv()
# Debug desactivado para producción
DEBUG = True

# Hosts permitidos en producción
#ALLOWED_HOSTS = ['entraditaback-production.up.railway.app']
ALLOWED_HOSTS = ['entraditabackend.up.railway.app']

# Configuración de la base de datos SQLite para producción
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}     

# Orígenes de CORS específicos para producción
CORS_ALLOWED_ORIGINS = [
    'https://entraditafrontend-production.up.railway.app',
    'https://www.entraditafrontend-production.up.railway.app',
    'https://www.entradita.com',
    'https://www.entradita.net',
    'https://www.entradita.app',
    'https://www.entradita.com.ar',
]

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
        'https://entraditafrontend-production.up.railway.app',
    'https://www.entraditafrontend-production.up.railway.app',
    'https://www.entradita.com',
    'https://www.entradita.net',
    'https://www.entradita.app',
    'https://www.entradita.com.ar',
]

CORS_ALLOW_CREDENTIALS = True
