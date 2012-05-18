import os, sys
from django.conf import settings

DIRNAME = os.path.dirname(__file__)
print settings.configured
settings.configure(DEBUG = True,
                   DATABASE_ENGINE = 'django.db.backends.sqlite3',
                   DATABASE_NAME = os.path.join(DIRNAME, 'database.db'),
                   INSTALLED_APPS = ('django.contrib.auth',
                                     'django.contrib.contenttypes',
                                     'django.contrib.sessions',
                                     'django.contrib.admin',
                                     'bootstrap',
                                     'bootstrap.tests',))


from django.test.simple import DjangoTestSuiteRunner

tr = DjangoTestSuiteRunner(verbosity=1)
failures = tr.run_tests(['bootstrap',])
if failures:
    sys.exit(failures)
