from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-mi2cv#je8*$3etxpse5)e6u^jhgiziu(n-akwm*g#c8bl8tpl9'

DEBUG = True

ALLOWED_HOSTS = ["*"]



INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
    'users.apps.UsersConfig',

]


CSRF_TRUSTED_ORIGINS = [
    "http://vault.aknet.kg",
    "https://vault.aknet.kg",
    "http://127.0.0.1",
    "http://localhost",
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

ROOT_URLCONF = 'vault.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vault.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}



LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

USE_TZ = False

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'


LOGIN_REDIRECT_URL = 'core'

LOGOUT_REDIRECT_URL = 'core'

LOGIN_URL ='users:login'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.authentication.EmailAuthBackend',
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


EMAIL_HOST = "smtp.mail.ru"
EMAIL_PORT = 465
EMAIL_HOST_USER = "vault.official@mail.ru"
EMAIL_HOST_PASSWORD= "nG9iHEBYnQxg03kt9bke"
EMAIL_USE_SSL = True

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER

AUTH_USER_MODEL = 'users.User'


DEFAULT_USER_IMAGE = MEDIA_URL + "users/default.png"



ASGI_APPLICATION = 'vault.asgi.application'
