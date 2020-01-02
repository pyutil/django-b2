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

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_b2.apps.DjangoB2Config',
        ...
    )

Add django-b2's URL patterns:

.. code-block:: python

    from django_b2 import urls as django_b2_urls


    urlpatterns = [
        ...
        url(r'^', include(django_b2_urls)),
        ...
    ]

Features
--------

* TODO

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
