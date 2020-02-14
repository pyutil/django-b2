# django-b2
django backblaze b2 storage using b2sdk (can be used outside of django for upload/download single files too)

## Install

Install the last stable release

    pip install django-b2

Create bucket at backblaze.com. No need for older versions of saved files:
While royendgel/django-backblazeb2-storage uses older versions, django-b2 will always rename to unique filename. 

Add this to Django settings

    MEDIA_URL = '/media/'
    DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'                 # if used without django-tenant-schemas
    # DEFAULT_FILE_STORAGE = 'django_b2.tenant_storage.TenantB2Storage'  # if used with django-tenant-schemas
    B2_APP_KEY_ID=000xxxxxxxxxxxx000000000n
    B2_APP_KEY=keyvalue
    B2_BUCKET_NAME=bucketname
    # optional, see docs, Usage:
    MEDIA_ROOT = ..
    B2_LOCAL_MEDIA = ..  # "", "M", "L", "ML"

Of course B2_.. values should never be published.
Don't upload the settings file to public sites (github, ..) or use some technique to hide the secret parameters.
This can be environment variables or hidden config file. You can see tests/test_B2Storage.py for ideas.

### Imagekit which need reopen the picture soon (Wagtail or so), local filesystem cache

If you upload an image and the imagekit want to reopen it immediately (to create thumbnails or so) it can fail
because backblaze storage has the file not immediately accessible.
We handle this that way that you can add B2_LOCAL_MEDIA into your settings.

    B2_LOCAL_MEDIA='ML'

M means that the copy of file is saved to the local filesystem MEDIA_ROOT too and the file is opened from this local "cache".
That way the files are soon and faster accessible.
L means that a log files are written into <MEDIA_ROOT>/_log.
With help of logs (files in _log directory) the locally cached files can be deleted: one hour later or 5 days later.

There is a script (django management command) b2_clear_local_media usable via cron, celery,..
It will delete local media files older than few hours or days. Later they will be served from backblaze.

### Using outside of Django

Don't use the storage.py file. Use the backblaze_b2.py only.

    from django_b2.backblaze_b2 import BackBlazeB2
    b2 = BackBlazeB2()
    b2.authorize("production", application_key_id, application_key)
    b2.set_bucket(bucket_name)
    with open(filename, 'rb') as f:
        b2.upload_file(filename, f)
    content = b2.download_file(filename)
    with open(filename2, 'wb') as f:
        f.write(content)

### Large uploads

Nginx large file uploads:
You need at least modify /etc/nginx/nginx.conf, http section, add client_... settings.

Read: https://vsoch.github.io/2018/django-nginx-upload/

Example:

    client_max_body_size 100M;
    client_body_buffer_size 100M;
    client_body_timeout 120;

### Upload (backup) single file (new in 0.2.0)

This is implemented in backblaze_b2.py file if called as script.
We don't implement it (yet) as the django management command. That means outside of Django: You can use this too.
And in Django: No need (at 0.2.0) to add this package to INSTALLED_APPS.

You can describe the target bucket in environment variables or in the .ini file. For details:

    python (path/)backblaze_b2.py --help

### Backup the postgres database (new in 0.2.0)

Once django-b2 is installed, pgtob2.sh script is available in the virtual environment.
Write 'which pgtob2.sh' for its location.
See comments inside the script for more info.  
    

## Developers

Upload and Download methods work, but probably very stupid and non-effective.
If you understand the problem more, please help rewrite them and send pull request:
- fork pyutil/django-b2,
- clone your fork,
- set upstream in git config to pyutil/,
- arrange virtual environment and install (pip install -r ...) requirements.txt & requirements_dev.txt,
- don't touch "master" branch so you can always pull pyutil/ upstream,
- create a "fork" branch where you can always merge "master" and feature branches,
- create a "<feature>" branch(es) for every single change,
- commit+push "<feature>" branch,
- in github web interface generate a pull request,
- merge "<feature>" branch into "fork" branch (optional)
(maybe you have better idea how to arrange branches in your fork)

## Tests

Install test requirements inside your virtual environment

    pip install -r requirements_test.txt

Create a backblaze bucket.
Set B2_.. environment variables or a config file /etc/django/test-django-b2/env.ini - see tests/test_B2Storage.py.
Run pytest.
Alternatively you can run tox:
You could install pyenv system-wide, pyenv install required 3.N python versions (see tox.ini).
Then in the project dir: pyenv local 3.x.x 3.y.y 3.z.z
And run: tox
