=====
Usage
=====

Django

Add this to Django settings

.. code-block:: python

    MEDIA_URL = '/media/'
    DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'
    B2_APP_KEY_ID=000xxxxxxxxxxxx000000000n
    B2_APP_KEY=keyvalue
    B2_BUCKET_NAME=bucketname


Without Django:

You can upload/download single files. This is not suitable for mass backups, see backblaze docs.

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
