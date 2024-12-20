# entradita/settings/production.py

from .base import *
import dj_database_url
from dotenv import load_dotenv
import os

load_dotenv()
# Debug desactivado para producción
DEBUG = False

# Hosts permitidos en producción
ALLOWED_HOSTS = ['entraditaback-develop.up.railway.app']
# Base de datos de producción (URL en variable de entorno)

# Configuración de la base de datos SQLite para producción
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}
# Orígenes de CORS específicos para producción
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://www.entradita-frontend-git-develop-aguilarzzs-projects.vercel.app",
]

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = ['https://entraditaback-develop.up.railway.app']
