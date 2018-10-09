import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '9z1&*gt_r8v)llrfi9lkldar6$eofs(1=1_5q(cl7^d-9h27=r'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'payments.apps.PaymentsConfig',
    'django.contrib.contenttypes',
]

MIDDLEWARE = []

ROOT_URLCONF = 'coinsph_assignment.urls'

WSGI_APPLICATION = 'coinsph_assignment.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = False
