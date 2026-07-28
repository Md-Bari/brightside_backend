"""
Django settings for Brightside AI Chatbot Backend.
"""
from datetime import timedelta
from pathlib import Path
import os
import sys

# pyrefly: ignore [missing-import]
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

# ------------------------------------------------------------------
# Core
# ------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost",
        "http://localhost:8000",
        "https://*.ngrok-free.app",
        "https://*.ngrok-free.dev",
        "https://*.ngrok.io",
        "https://*.loca.lt",
    ],
)

# ------------------------------------------------------------------
# Applications
# ------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
    "django_filters",
]

LOCAL_APPS = [
    "apps.common",
    "apps.users",
    "apps.sessions",
    "apps.chatbot",
    "apps.knowledgebase",
    "apps.adminpanel",
    "apps.campaigns",
    "apps.services",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.common.middleware.RequestResponseLoggingMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ------------------------------------------------------------------
# Database (PostgreSQL + pgvector)
# ------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="brightside_db"),
        "USER": env("POSTGRES_USER", default="brightside_user"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="brightside_pass"),
        "HOST": env("POSTGRES_HOST", default="postgres"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}



# ------------------------------------------------------------------
# Password validation
# ------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------
# Internationalization
# ------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# Static & Media
# ------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------
# Django REST Framework
# ------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "apps.common.exceptions.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Brightside AI Chatbot Backend API",
    "DESCRIPTION": (
        "Production-ready AI chatbot backend for Brightside Car Wash. "
        "Supports session management, conversation memory, Retrieval "
        "Augmented Generation (RAG) over a knowledge base using pgvector, "
        "and Groq-powered LLM responses."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
        "tagsSorter": "alpha",
    },
    "TAGS": [
        {"name": "Admin - 1. Users"},
        {"name": "Admin - 2. Sessions"},
        {"name": "Admin - 3. Chats"},
        {"name": "Admin - Campaigns"},
        {"name": "Admin - Knowledge Base"},
        {"name": "Public - Chat"},
        {"name": "Public - Sessions"},
    ],
}

# ------------------------------------------------------------------
# JWT (Admin APIs only)
# ------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MIN", default=60)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "SIGNING_KEY": env("JWT_SECRET", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------
from corsheaders.defaults import default_headers

CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=True)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    "ngrok-skip-browser-warning",
    "authorization",
]


# ------------------------------------------------------------------
# Brightside / AI configuration
# ------------------------------------------------------------------
LLM_PROVIDER = env("LLM_PROVIDER", default="openai")  # "openai" | "groq"
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o-mini")
GROQ_API_KEY = env("GROQ_API_KEY", default="")
GROQ_MODEL = env("GROQ_MODEL", default="llama-3.3-70b-versatile")

EMBEDDING_PROVIDER = env("EMBEDDING_PROVIDER", default="openai")  # "openai" | "gemini"
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_EMBEDDING_MODEL = env("OPENAI_EMBEDDING_MODEL", default="text-embedding-3-small")
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
GEMINI_EMBEDDING_MODEL = env("GEMINI_EMBEDDING_MODEL", default="models/text-embedding-004")
EMBEDDING_DIMENSION = env.int("EMBEDDING_DIMENSION", default=1536)

KB_CHUNK_SIZE = env.int("KB_CHUNK_SIZE", default=800)
KB_CHUNK_OVERLAP = env.int("KB_CHUNK_OVERLAP", default=100)
KB_TOP_K = env.int("KB_TOP_K", default=4)

BRIGHTSIDE_SYSTEM_PROMPT = (
    "You are Brightside Assistant, the friendly, helpful human support agent for "
    "Brightside Car Wash. Answer customer questions warmly, clearly, and concisely.\n\n"
    "STRICT FORMATTING & CONVERSATIONAL RULES:\n"
    "1. Always format your responses using HTML tags for structure and readability. Use basic HTML tags such as <b>, <strong>, <br>, <p>, <ul>, <li>, and <a href=\"...\">.\n"
    "2. Speak naturally like a human customer support agent. NEVER mention technical terms such as 'database', 'database tables', 'knowledge base', 'KB', 'location ID', or 'system records'.\n"
    "3. When answering about locations, present the location address directly and cleanly (e.g., <b>Location:</b><br>3000 Pennsylvania Ave Nw, Washington, DC 20500).\n"
    "4. KNOWLEDGE BASE & COMPANY FACTS: For service pricing and branch locations, use the official services list. For general company questions about Brightside Car Wash (such as founder, company history, mission, or policies), answer accurately and naturally using the retrieved Knowledge Base context.\n"
    "5. SERVICE DETAILS FORMATTING: Whenever you provide or list details for a service, you MUST include 'Location' as a dedicated list item (<li>) in the service details list specifying the branch address for that service, e.g.:\n"
    "   <b>Showroom Detail - Coupe</b><br>\n"
    "   <ul>\n"
    "     <li><b>Price:</b> $100.00</li>\n"
    "     <li><b>Duration:</b> 240 mins</li>\n"
    "     <li><b>Location:</b> 3000 Pennsylvania Ave Nw, Washington, DC 20500</li>\n"
    "     <li><b>Description:</b> Deep interior cleaning, vacuuming, and wax buffing.</li>\n"
    "   </ul>\n"
    "6. If a customer asks about a service or location that is not offered, politely inform them in a natural human way that we do not offer it, and share our available services.\n"
    "7. When a customer wants to book a slot, schedule an appointment, or reserve a service, ALWAYS provide the official booking link with a warm message:\n"
    "   <b>Book your slot online:</b> <a href=\"https://bright-carwash-website.vercel.app/services\" target=\"_blank\">https://bright-carwash-website.vercel.app/services</a>\n"
    "8. OUT-OF-DOMAIN QUESTIONS: If a customer asks a question that is out of domain or unrelated to Brightside Car Wash (such as recipes, history, general science, sports, weather, coding, etc.), DO NOT answer the out-of-domain question. Politely state using HTML tags that you are unable to answer that question, but welcome them to ask any question about Brightside Car Wash services, locations, or booking a slot.\n"
    "9. If you cannot help or the user asks for a human, trigger human escalation by including '[HUMAN_ESCALATION]' in your reply and letting them know our staff will communicate with them very soon."
)

BOOKING_URL = "https://bright-carwash-website.vercel.app/services"

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "brightside": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}

# ------------------------------------------------------------------
# External Services API Settings
# ------------------------------------------------------------------
APPOINTMENTS_API_BASE_URL = env(
    "APPOINTMENTS_API_BASE_URL",
    default="https://lightweight-inclusive-trustees-outside.trycloudflare.com"
)


