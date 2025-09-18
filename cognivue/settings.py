# cognivue/settings.py
from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')



def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, "True" if default else "False").lower() in {"1", "true", "yes", "on"}

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
DEBUG = env_bool("DEBUG", False)


ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]


CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if "." in h]
if "localhost" in ALLOWED_HOSTS or "127.0.0.1" in ALLOWED_HOSTS:
    CSRF_TRUSTED_ORIGINS += ["http://localhost", "http://127.0.0.1"]


ALLOW_SCRAPER = env_bool("ALLOW_SCRAPER", False)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")



INSTALLED_APPS = [
    "corsheaders",
    "cognivue.news_scraper",
    "cognivue.timer",
    "cognivue.vitamin_d_helper",
    "django_countries",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "cognivue.insights",
    'cognivue.nutrition',

]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cognivue.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cognivue.wsgi.application"



if os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.parse(
            os.environ["DATABASE_URL"],
            conn_max_age=600,
        )
    }
else:
    
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PG_DB", "cognivue"),
            "USER": os.getenv("PG_USER", "cognivue"),
            "PASSWORD": os.getenv("PG_PASS", ""),
            "HOST": os.getenv("PG_HOST", "127.0.0.1"),
            "PORT": os.getenv("PG_PORT", "5432"),
            "OPTIONS": {
            "sslmode": "disable",   
        },
        }
    }



AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]



LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True



STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"



SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGOUT_REDIRECT_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/vitamin-d-helper/"

# CORS settings for frontend integration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5176",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only allow all origins in debug mode

# Allow specific headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
