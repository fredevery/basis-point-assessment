from .settings import *

# Production-specific settings
DEBUG = False
ALLOWED_HOSTS = [os.getenv("DJANGO_ALLOWED_HOSTS", "example.com").split(",")]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", SECRET_KEY)

# Optionally override database or other settings here
# Example:
# DATABASES["default"]["HOST"] = os.getenv("POSTGRES_HOST", "db")
