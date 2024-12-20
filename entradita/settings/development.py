# entradita/settings/development.py

from .base import *
import dj_database_url
from dotenv import load_dotenv
import os

load_dotenv()
# Debug activado para desarrollo
DEBUG = True
# Hosts permitidos en desarrollo
ALLOWED_HOSTS = ['*']
# Base de datos local
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}
# Orígenes CORS permitidos para desarrollo
CORS_ALLOW_ALL_ORIGINS = True


