# entradita/settings/production.py

from .base import *
import dj_database_url

# Debug desactivado para producción
DEBUG = False

# Hosts permitidos en producción
ALLOWED_HOSTS = ['entraditaback-production.up.railway.app']
# Base de datos de producción (URL en variable de entorno)
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}
# Orígenes de CORS específicos para producción
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://www.entradita.com",
]

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = ['https://entraditaback-production.up.railway.app']
