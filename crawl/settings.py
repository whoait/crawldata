"""
Django settings for auto_translation project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from __future__ import absolute_import
import os
from django.conf import global_settings

PROJ_PATH = os.path.dirname(os.path.dirname(__file__))
PROJ_PARENT_PATH = os.path.normpath(os.path.join(PROJ_PATH, ".."))
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w+2edfb4@b+!x6geln(%99yu+%^kev@n5g#8+ewry-agb2v0x%'

ADMIN_PATH = 'admin'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

HTTP_HOST = "fiuzu.com"
ALLOWED_HOSTS = ['localhost',
                 'prod.' + HTTP_HOST,
                 '127.0.0.1', HTTP_HOST,
                 'www.' + HTTP_HOST, ]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crawl',
    'thebesttimetovisit',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'crawl.urls'

WSGI_APPLICATION = 'crawl.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(PROJ_PARENT_PATH, 'crawl.cnf'),
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJ_PATH, "static"),
)

STATICFILES_FINDERS = global_settings.STATICFILES_FINDERS + (
    'compressor.finders.CompressorFinder',
)

SUIT_CONFIG = {
    'ADMIN_NAME': 'Fiuzu Crawling Data Admin',

    'CONFIRM_UNSAVED_CHANGES': False,
    'MENU_OPEN_FIRST_CHILD': True,
    'MENU': (
         'sites',
         {'app': 'auth', 'icon':'icon-lock', 'models': ('group'), 'label': 'Authentication'},
         # {'app': 'crawl',
         #    'icon':'icon-user',
         #    'models': (
         #        'dbconfig',
         #    ),
         #    'label': 'DB Config'},
        '-',
         {'label': 'Tools', 'url': '/%s/tools/home/' % ADMIN_PATH, 'icon':'icon-wrench'},
         {'label': 'Support', 'icon':'icon-question-sign', 'url': 'mailto:tung@fiuzu.com'},
    ),
}

PROFILE_LOG_BASE =  os.path.join(PROJ_PARENT_PATH, 'logs')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] %(process)d %(thread)d %(module)s %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'null': {
            # Note: The level doesn't matter since it goes into a blackhole.
            'level': 'ERROR',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': PROFILE_LOG_BASE + "/visahq.log",
            'formatter': 'simple',
        },
    },
    'loggers': {
        # for manually triggered commands
        'commands': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': True,
        }
    }
}
####DOGSLOW LOGGING #########
# Watchdog is enabled by default, to temporarily disable, set to False:
DOGSLOW = True

# By default, Watchdog will create log files with the backtraces.
# You can also set the location of where it stores them:
DOGSLOW_LOG_TO_FILE = True
DOGSLOW_OUTPUT = '/tmp'

# Log requests taking longer than 25 seconds:
DOGSLOW_TIMER = 35

# Print (potentially huge!) local stack variables (off by default, use
# True for more detailed, but less manageable reports)
DOGSLOW_STACK_VARS = True
####END DOGSLOW #############

os.environ['SCRAPY_SETTINGS_MODULE'] = 'thebesttimetovisit.settings'