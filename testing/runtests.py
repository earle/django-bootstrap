import os, sys
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'testing.settings'

from django.test.simple import DjangoTestSuiteRunner

tr = DjangoTestSuiteRunner(verbosity=1)
failures = tr.run_tests(['bootstrap',])
if failures:
    sys.exit(failures)
