=============================
django-b2
=============================

.. image:: https://badge.fury.io/py/django-b2.svg
    :target: https://badge.fury.io/py/django-b2

.. image:: https://travis-ci.org/pyutil/django-b2.svg?branch=master
    :target: https://travis-ci.org/pyutil/django-b2

.. image:: https://codecov.io/gh/pyutil/django-b2/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/pyutil/django-b2

django backblaze b2 storage using b2sdk (b2sdk is official backblaze python library)

Documentation
-------------

The full documentation is at https://django-b2.readthedocs.io.

Quickstart
----------

Install django-b2::

    pip install django-b2

Add into your settings:

.. code-block:: python

    MEDIA_URL = '/media/'
    DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'
    B2_APP_KEY_ID=000xxxxxxxxxxxx000000000n
    B2_APP_KEY=keyvalue
    B2_BUCKET_NAME=bucketname
    # optional, see Usage:
    MEDIA_ROOT = ..
    B2_LOCAL_MEDIA = ..  # "", "M", "L", "ML"

Using outside of Django:

.. code-block:: python

    from django_b2.backblaze_b2 import BackBlazeB2
    b2 = BackBlazeB2()
    b2.authorize("production", application_key_id, application_key)
    b2.set_bucket(bucket_name)
    with open(filename, 'rb') as f:
        b2.upload_file(filename, f)
    content = b2.download_file(filename)
    with open(filename2, 'wb') as f:
        f.write(content)


Features
--------

- Django media storage (with storage.py) or general python access to BackBlaze B2 (without usage of storage.py).
- Upload single file to B2 (call backblaze_b2.py as script; new in 0.2.0)
- Backup a postgres database to B2 (use script pgtob2.sh; new in 0.2.0)
- Optionally cache media files locally for immediate access or for long time faster access.

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  b2sdk_
*  cookiecutter_
*  `cookiecutter-djangopackage`_

.. _b2sdk: https://github.com/Backblaze/b2-sdk-python
.. _cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
