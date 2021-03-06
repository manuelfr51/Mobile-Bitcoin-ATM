"""
Django settings for bitcash project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import re
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
LOCALE_PATHS = (PROJECT_PATH + "/locale/",)
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
# Another good one: https://github.com/etianen/django-herokuapp#validating-your-heroku-setup


SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv('DEBUG') == 'True':
    DEBUG = True
else:
    DEBUG = False
if os.getenv('TEMPLATE_DEBUG') == 'True':
    TEMPLATE_DEBUG = True
else:
    TEMPLATE_DEBUG = False

ALLOWED_HOSTS = (
    'www.coinsafe.com',
    '.coinsafe.com',
    'coinsafe.herokuapp.com',
    'www.closecoin.com',
    '.closecoin.com',
    'closecoin.herokuapp.com',
    'bitcashstaging.herokuapp.com',
    '127.0.0.1',
    )

ADMINS = (
    ('Michael Flaxman', 'michael@coinsafe.com'),
    ('Tom Chokel', 'tom@coinsafe.com'),
)

IGNORABLE_404_URLS = (
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'raven.contrib.django.raven_compat',
    'polymorphic',
    'south',
    'storages',
    'crispy_forms',
    'users',
    'merchants',
    'bitcoins',
    'shoppers',
    'services',
    'emails',
    'phones',
    'credentials',
    'coinbase_wallets',
    'bitstamp_wallets',
    'blockchain_wallets',
    'profiles',
    'blog',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'bitcash.middleware.AjaxMessaging',
    'bitcash.middleware.ImpersonateMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'bitcash.middleware.MerchantAdminSectionMiddleware',
    'django_otp.middleware.OTPMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'bitcash.context_processors.credential_status',
)

AUTH_USER_MODEL = 'users.AuthUser'


PRODUCTION_DOMAIN = 'www.coinsafe.com'
STAGING_DOMAIN = 'bitcashstaging.herokuapp.com'
SITE_DOMAIN = os.getenv('SITE_DOMAIN', PRODUCTION_DOMAIN)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# SSL and BASE_URL settings for Production, Staging and Local:
if SITE_DOMAIN in (PRODUCTION_DOMAIN, STAGING_DOMAIN):
    BASE_URL = 'https://%s' % SITE_DOMAIN
    # SSL stuff:
    # FIXME: fix this
    # SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    MIDDLEWARE_CLASSES += ('bitcash.middleware.SSLMiddleware',)
else:
    # FIXME: this should work on staging too, but I can't get it to work with gunicorn
    DEBUG_TOOLBAR_PATCH_SETTINGS = True
    BASE_URL = 'http://%s' % SITE_DOMAIN


IS_PRODUCTION = (SITE_DOMAIN == PRODUCTION_DOMAIN)

if IS_PRODUCTION:
    EMAIL_DEV_PREFIX = False
else:
    EMAIL_DEV_PREFIX = True
    # Enable debug toolbar on local and staging
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES
    INSTALLED_APPS += ('debug_toolbar', )

SESSION_EXPIRE_AT_BROWSER_CLOSE = True


ROOT_URLCONF = 'bitcash.urls'

WSGI_APPLICATION = 'bitcash.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# Parse database configuration from $DATABASE_URL
import dj_database_url
# http://stackoverflow.com/a/11100175
DJ_DEFAULT_URL = os.getenv('DJ_DEFAULT_URL', 'postgres://localhost')
DATABASES = {'default': dj_database_url.config(default=DJ_DEFAULT_URL)}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
# LANGUAGE_CODE = 'es'
LANGUAGES = (
    ('en-us', 'English'),
    ('es', 'Spanish'),
    ('cs', 'Czech'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Yay crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap', 'bootstrap3')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
# # Static asset configuration
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
TEMPLATE_DIRS = (os.path.join(PROJECT_PATH, 'templates'),)

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# http://blog.iambob.me/the-super-stupid-idiots-guide-to-getting-started-with-django-pipeline-and-s3/
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
assert AWS_ACCESS_KEY_ID
assert AWS_SECRET_ACCESS_KEY
assert AWS_STORAGE_BUCKET_NAME

BCI_SECRET_KEY = os.getenv('BCI_SECRET_KEY')
assert BCI_SECRET_KEY, 'Must have BCI_SECRET_KEY (to create BCI wallets)'

CHAIN_COM_API_KEY = os.getenv('CHAIN_COM_API_KEY')
assert CHAIN_COM_API_KEY, 'Must have CHAIN_COM_API_KEY (to create make chain.com API calls)'

BLOCKCYPHER_API_KEY = os.getenv('BLOCKCYPHER_API_KEY')

SERVER_EMAIL = 'support@coinsafe.com'

# For transactional messages:
POSTMARK_SMTP_SERVER = 'smtp.postmarkapp.com'
POSTMARK_SENDER = 'CoinSafe Support <support@coinsafe.com>'
POSTMARK_TEST_MODE = os.getenv('POSTMARK_TEST_MODE', False)
POSTMARK_API_KEY = os.getenv('POSTMARK_API_KEY')
assert POSTMARK_API_KEY, 'Must have a Postmark API Key'

# For marketing messages:
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN', 'coinsafe.com')
assert MAILGUN_API_KEY, 'Must have a Mailgun API Key'
assert MAILGUN_DOMAIN, 'Must have a Mailgun Domain'

BCC_DEBUG_ADDRESS = 'CoinSafeBCC@gmail.com'

EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'

PLIVO_AUTH_TOKEN = os.getenv('PLIVO_AUTH_TOKEN')
PLIVO_AUTH_ID = os.getenv('PLIVO_AUTH_ID')
assert PLIVO_AUTH_ID, 'Must have plivo API access'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/app/'

MERCHANT_LOGIN_REQUIRED_PATHS = ['/transactions/', '/merchant-settings/', '/profile/', '/wallet/', '/edit-personal-info/', '/edit-hours-info/', '/edit-merchant-info/', '/edit-btc-info/']
MERCHANT_LOGIN_PW_URL = '/password/'

CAPITAL_CONTROL_COUNTRIES = ['ARS', 'VEF']

# http://scanova.io/blog/engineering/2014/05/21/error-logging-in-javascript-and-python-using-sentry/
LOGGING = {
    'version': 1,
    # https://docs.djangoproject.com/en/dev/topics/logging/#configuring-logging
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# Keep this at the end
if DEBUG:
    print '-' * 75
    print 'SITE_DOMAIN is set to %s' % SITE_DOMAIN
    print "If you're testing webhooks, be sure this is correct"
    print '-' * 75
