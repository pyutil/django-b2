"""
    configure HIDDEN_SETTINGS file (see bellow), section [b2], B2_APP_KEY_ID=000xx..., B2_APP_KEY=.., B2_BUCKET_NAME=..

    alternatively if this is not possible set the environment variables with same names
"""

import os
from configparser import RawConfigParser, NoSectionError
from unittest import TestCase

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_b2.storage import B2Storage


HIDDEN_SETTINGS = '/etc/django/test-django-b2/env.ini'


settings.configure()

config = RawConfigParser()
config.read(HIDDEN_SETTINGS)


class TestB2(TestCase):
    def testB2Storage(self):
        try:
            settings.B2_APP_KEY_ID = (os.environ.get('MZ_B2_APP_KEY_ID') or os.environ.get('B2_APP_KEY_ID')
                                      or config.get('b2', 'B2_APP_KEY_ID'))
            settings.B2_APP_KEY = (os.environ.get('MZ_B2_APP_KEY') or os.environ.get('B2_APP_KEY')
                                   or config.get('b2', 'B2_APP_KEY'))
            settings.B2_BUCKET_NAME = (os.environ.get('MZ_B2_BUCKET_NAME') or os.environ.get('MZ_B2_BUCKET_NAME')
                                       or config.get('b2', 'B2_BUCKET_NAME'))
        except NoSectionError:
            raise ImproperlyConfigured('Configure .ini file or set environment variables - see test_B2Storage.py.')

        st = B2Storage()

        assert st.listdir('') == ([], []),\
                'bucket %s is not empty, please login to backblaze.com and clear it completely'\
                % settings.B2_BUCKET_NAME
