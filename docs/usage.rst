=====
Usage
=====

**Django**:

Add this to Django settings

.. code-block:: python

    MEDIA_URL = '/media/'
    DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'
    B2_APP_KEY_ID=000xxxxxxxxxxxx000000000n
    B2_APP_KEY=keyvalue
    B2_BUCKET_NAME=bucketname


**Large uploads**:

Nginx large file uploads:
You need at least modify /etc/nginx/nginx.conf, http section, add client... settings.

Read: https://vsoch.github.io/2018/django-nginx-upload/

Example:
    client_max_body_size 100M;
    client_body_buffer_size 100M;
    client_body_timeout 120;

**Imagekit which need reopen the picture soon (Wagtail or so), local filesystem cache**

If you upload an image and the imagekit want to reopen it immediately (to create thumbnails or so) it can fail
because backblaze storage has the file not immediately accessible.
We handle this that way that you can add B2_LOCAL_CACHE into your settings.

    B2_LOCAL_CACHE='FM'

F means that the copy of file is saved to the local filesystem MEDIA_ROOT too and the file is opened from this local "cache".
That way the files are soon and faster accessible.
M means that a log files are written into <MEDIA_ROOT>/_meta.
With help of logs (_meta files) the locally cached files can be deleted: one hour later or 5 days later.

TODO: The cache cleaning script will be implemented (and you will be able call it via cron, celery, ..)
but this is not done in 0.3.0 yet.
Feel free to delete older media files in local file system by hand: they will be served from backblaze.

Or without deleting of local media files you can simple have local instances backuped on backblaze.

**Without Django**:

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

**Upload/backup single file to b2 from console**:

This is implemented in backblaze_b2.py file if called as script.
We don't implement it (yet) as the django management command. That means outside of Django: You can use this too.
And in Django: No need (at 0.2.0) to add this package to INSTALLED_APPS.

You can describe the target bucket in environment variables or in the .ini file. For details:

.. code-block:: bash

    python (path/)backblaze_b2.py --help

**Backup the postgres database**:

Once django-b2 is installed, pgtob2.sh script is available in the virtual environment.
Write 'which pgtob2.sh' for its location.
Read comments inside the script for more info.
