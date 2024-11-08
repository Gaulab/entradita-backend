# entradita/settings/development.py

from .base import *

# Debug activado para desarrollo
DEBUG = True
# Hosts permitidos en desarrollo
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
# Base de datos local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Orígenes CORS permitidos para desarrollo
CORS_ALLOW_ALL_ORIGINS = True


