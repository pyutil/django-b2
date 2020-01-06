"""
    configure HIDDEN_SETTINGS file (see bellow), section [b2], B2_APP_KEY_ID=000xx..., B2_APP_KEY=.., B2_BUCKET_NAME=..

    alternatively if this is not possible set the environment variables with same names
"""

import os
from configparser import RawConfigParser, NoSectionError
from datetime import datetime, timedelta
from tempfile import SpooledTemporaryFile
from unittest import TestCase

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_b2.storage import B2Storage


HIDDEN_SETTINGS_AS_FILE = '/etc/django/test-django-b2/env.ini'


settings.configure()

config = RawConfigParser()
config.read(HIDDEN_SETTINGS_AS_FILE)


class TestB2(TestCase):
    def testB2Storage(self):
        try:
            settings.B2_APP_KEY_ID = os.environ.get('B2_APP_KEY_ID') or config.get('b2', 'B2_APP_KEY_ID')
            settings.B2_APP_KEY = os.environ.get('B2_APP_KEY') or config.get('b2', 'B2_APP_KEY')
            settings.B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME') or config.get('b2', 'B2_BUCKET_NAME')
        except NoSectionError:
            raise ImproperlyConfigured('Configure .ini file or set environment variables - see test_B2Storage.py.')

        st = B2Storage()
        st.b2.purge_bucket()  # maybe previous test has failed?
        assert st.listdir('') == ([], [])
        dt = datetime.now()

        fullname = 'dir1/file1'
        content = b'12345'
        assert not st.exists(fullname)

        with SpooledTemporaryFile() as tempf:
            tempf.write(content)
            tempf.seek(0)
            st._save(fullname, tempf)
        assert st.listdir('') == (['dir1'], [])
        assert st.listdir('dir1') == ([], ['file1'])
        assert st.exists(fullname)
        assert st.size(fullname) == len(content)
        assert st.get_created_time(fullname) == st.get_modified_time(fullname)
        assert st.get_created_time(fullname) == st.get_accessed_time(fullname)
        assert dt - timedelta(seconds=10) <= st.get_created_time(fullname) <= datetime.now() + timedelta(seconds=10)
        assert ('/%s?Authorization=' % fullname) in st.url(fullname)  # if fails: is bucket Private?
        assert st._open(fullname).read() == content

        st.delete(fullname)
        # not needed as long as we have single file in the test
        # st.b2.purge_bucket()  # cleanup

        assert st.listdir('') == ([], [])
