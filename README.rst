=============================
django-b2
=============================

.. image:: https://badge.fury.io/py/django-b2.svg
    :target: https://badge.fury.io/py/django-b2

.. image:: https://travis-ci.org/pyutil/django-b2.svg?branch=master
    :target: https://travis-ci.org/pyutil/django-b2

.. image:: https://codecov.io/gh/pyutil/django-b2/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/pyutil/django-b2

django backblaze b2 storage using b2sdk

Documentation
-------------

The full documentation is at https://django-b2.readthedocs.io.

Quickstart
----------

Install django-b2::

    pip install django-b2

Add itno your settings:

.. code-block:: python

    DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'
    B2_APP_KEY_ID=000xxxxxxxxxxx000000000n    # application key ID
    B2_APP_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # application key value
    B2_BUCKET_NAME=xxxxxxxxxxxxx              # bucketname

Features
--------

Django media storage (with storage.py) or general python access to BackBlaze B2 (without use of storage.py).

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
