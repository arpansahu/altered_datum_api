from pathlib import Path
from datetime import timedelta
import os
from decouple import config
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import django
from django.db.models.signals import pre_init

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================ENV VARIABLES=====================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(' ')
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
BUCKET_TYPE = config('BUCKET_TYPE')

DATABASE_URL = config('DATABASE_URL')
REDIS_CLOUD_URL = config('REDIS_CLOUD_URL')

MAIL_JET_API_KEY = config('MAIL_JET_API_KEY')
MAIL_JET_API_SECRET = config('MAIL_JET_API_SECRET')
MAIL_JET_EMAIL_ADDRESS = config('MAIL_JET_EMAIL_ADDRESS')

# Domain and Protocol Configuration
if DEBUG:
    DOMAIN = config('DOMAIN', default='localhost:8004')
    PROTOCOL = config('PROTOCOL', default='http')
else:
    DOMAIN = config('DOMAIN')
    PROTOCOL = config('PROTOCOL')

SENTRY_ENVIRONMENT = config('SENTRY_ENVIRONMENT')  # production Or "staging", "development", etc.
SENTRY_DSH_URL = config('SENTRY_DSH_URL')

# Harbor Configuration
HARBOR_URL = config('HARBOR_URL', default='https://harbor.arpansahu.space')
HARBOR_USERNAME = config('HARBOR_USERNAME', default='admin')
HARBOR_PASSWORD = config('HARBOR_PASSWORD', default='')

PROJECT_NAME = 'altered_datum_api'
USE_S3 = config('USE_S3', default=True, cast=bool)
# ===============================================================================

INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
    'blog_api',
    'corsheaders',
    'accounts',
    # Oauth
    'oauth2_provider',
    'social_django',
    'drf_social_oauth2',
    'check_service_health'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Enable CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For serving static files in production
    # Optional middlewares:
    'django.middleware.locale.LocaleMiddleware',  # Handles language preferences
    'social_django.middleware.SocialAuthExceptionMiddleware',  # For handling social auth exceptions
]

ROOT_URLCONF = 'altered_datum_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Oauth
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'altered_datum_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': DB_NAME,
#         'USER': DB_USER,
#         'PASSWORD': DB_PASSWORD,
#         'HOST': DB_HOST,
#         'PORT': DB_PORT,
#     }
# }


# Parse database configuration from $DATABASE_URL
import dj_database_url

# DATABASES['default'] =  dj_database_url.config()
# updated
DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

if not USE_S3:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/media/'
else:
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='eu-north-1')
    
    # Common S3 settings
    AWS_S3_FILE_OVERWRITE = False  # Prevent overwriting files with the same name
    AWS_DEFAULT_ACL = None  # Ensure files are not public by default
    
    # Switch between MinIO and AWS S3
    if BUCKET_TYPE == 'MINIO':
        # MinIO/S3 Configuration
        AWS_QUERYSTRING_AUTH = False  # Don't add query parameters to URLs (use bucket policy instead)
        AWS_S3_SIGNATURE_VERSION = 's3v4'
        AWS_S3_USE_SSL = True
        AWS_S3_VERIFY = True
        AWS_S3_ADDRESSING_STYLE = 'path'  # Use path-style addressing for MinIO
        
        # MinIO API endpoint through nginx proxy (for upload/management operations)
        AWS_S3_ENDPOINT_URL = 'https://minioapi.arpansahu.space'
        
        # Custom domain for serving files (use API endpoint, not console)
        AWS_S3_CUSTOM_DOMAIN = f'minioapi.arpansahu.space/{AWS_STORAGE_BUCKET_NAME}'
    elif BUCKET_TYPE == 'AWS':
        AWS_S3_ENDPOINT_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
        AWS_S3_CUSTOM_DOMAIN = AWS_S3_ENDPOINT_URL
    elif BUCKET_TYPE == 'BLACKBLAZE':
        AWS_S3_REGION_NAME = 'us-east-005'
        AWS_S3_ENDPOINT = f's3.{AWS_S3_REGION_NAME}.backblazeb2.com'
        AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_ENDPOINT}'
        AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.backblazeb2.com'

    # Static and Media File Storage Settings
    AWS_STATIC_LOCATION = f'portfolio/{PROJECT_NAME}/static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'
    
    AWS_PUBLIC_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_PUBLIC_MEDIA_LOCATION}/'
    
    AWS_PROTECTED_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/protected'
    
    AWS_PRIVATE_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/private'

    # Use your custom storage classes with modern STORAGES dict
    STORAGES = {
        'default': {
            'BACKEND': f'{PROJECT_NAME}.storage_backends.PublicMediaStorage',
            'OPTIONS': {
                'location': AWS_PUBLIC_MEDIA_LOCATION,
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
                'endpoint_url': AWS_S3_ENDPOINT_URL,
                'access_key': AWS_ACCESS_KEY_ID,
                'secret_key': AWS_SECRET_ACCESS_KEY,
            },
        },
        'staticfiles': {
            'BACKEND': f'{PROJECT_NAME}.storage_backends.StaticStorage',
            'OPTIONS': {
                'location': AWS_STATIC_LOCATION,
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
                'endpoint_url': AWS_S3_ENDPOINT_URL,
                'access_key': AWS_ACCESS_KEY_ID,
                'secret_key': AWS_SECRET_ACCESS_KEY,
            },
        },
        'private': {
            'BACKEND': f'{PROJECT_NAME}.storage_backends.PrivateMediaStorage',
            'OPTIONS': {
                'location': AWS_PRIVATE_MEDIA_LOCATION,
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
                'endpoint_url': AWS_S3_ENDPOINT_URL,
                'access_key': AWS_ACCESS_KEY_ID,
                'secret_key': AWS_SECRET_ACCESS_KEY,
                'default_acl': 'private',
                'custom_domain': False,  # Disable custom domain for private files
            },
        },
    }

# Development settings (for local media/static handling)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (

        # 'oauth2_provider.ext.rest_framework.OAuth2Authentication',  # django-oauth-toolkit < 1.0.0
        # django-oauth-toolkit >= 1.0.0
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'drf_social_oauth2.authentication.SocialAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# Custom user model
AUTH_USER_MODEL = "accounts.NewUser"

# AUTHENTICATION_BACKENDS = (
#     'drf_social_oauth2.backends.DjangoOAuth2',
#     'django.contrib.auth.backends.ModelBackend',
# )

AUTHENTICATION_BACKENDS = (
    # Others auth providers (e.g. Google, OpenId, etc)

    # Facebook OAuth2
    'social_core.backends.facebook.FacebookAppOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',

    # drf_social_oauth2
    'drf_social_oauth2.backends.DjangoOAuth2',

    # Django
    'django.contrib.auth.backends.ModelBackend',
)

# Facebook configuration
SOCIAL_AUTH_FACEBOOK_KEY = ('466557594456589')
SOCIAL_AUTH_FACEBOOK_SECRET = ('30939be871946ecd824b4a9f9ac6051e')
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://localhost:3000/'

# Define SOCIAL_AUTH_FACEBOOK_SCOPE to get extra permissions from Facebook.
# Email is not sent by default, to get it, you must request the email permission.
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email'
}
SOCIAL_AUTH_USER_FIELDS = ['email', 'username', 'first_name', 'password']

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # During development only
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'in-v3.mailjet.com'
EMAIL_HOST_USER = MAIL_JET_API_KEY
EMAIL_HOST_PASSWORD = MAIL_JET_API_SECRET
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = MAIL_JET_EMAIL_ADDRESS

PASSWORD_RESET_TIMEOUT = 60


#Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_CLOUD_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': PROJECT_NAME
    }
}

# Get the current git commit hash
def get_git_commit_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    except Exception:
        return None

sentry_sdk.init(
    dsn=SENTRY_DSH_URL,
    integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                # signals_spans=True,
                # signals_denylist=[
                #     django.db.models.signals.pre_init,
                #     django.db.models.signals.post_init,
                # ],
                # cache_spans=False,
            ),
        ],
    traces_sample_rate=1.0,  # Adjust this according to your needs
    send_default_pii=True,  # To capture personal identifiable information (optional)
    release=get_git_commit_hash(),  # Set the release to the current git commit hash
    environment=SENTRY_ENVIRONMENT,  # Or "staging", "development", etc.
    # profiles_sample_rate=1.0,
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'sentry': {
            'level': 'ERROR',  # Change this to WARNING or INFO if needed
            'class': 'sentry_sdk.integrations.logging.EventHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'sentry'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'sentry'],
            'level': 'ERROR',  # Only log errors to Sentry
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'sentry'],
            'level': 'ERROR',  # Only log errors to Sentry
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',  # You can set this to INFO or DEBUG as needed
            'propagate': False,
        },
        # You can add more loggers here if needed
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
}

CSRF_TRUSTED_ORIGINS = [f'{PROTOCOL}://{DOMAIN}', f'{PROTOCOL}://*.{DOMAIN.split(":")[0]}']

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
#     'https://altered-datum.arpansahu.space',
# ]

CORS_ALLOW_ALL_ORIGINS = True