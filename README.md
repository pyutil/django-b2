# django-b2
django backblaze b2 storage using b2sdk (can be used outside of django for upload/download single files too)

## Install

Install the last stable release

    pip install django-b2

Create bucket at backblaze.com. No need for older versions:
While royendgel/django-backblazeb2-storage uses older versions, django-b2 will always rename to unique filename. 

Add this to Django settings

    MEDIA_URL = '/media/'
    DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'
    B2_APP_KEY_ID=000xxxxxxxxxxxx000000000n
    B2_APP_KEY=keyvalue
    B2_BUCKET_NAME=bucketname

Of course B2_.. values should never be published.
Don't upload the settings file to public sites (github, ..) or use some technique to hide the secret parameters.
This can be environment variables or hidden config file. You can see tests/test_B2Storage.py for ideas.

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

Nginx large file uploads:
You need at least modify /etc/nginx/nginx.conf, http section, add client_... settings.
Read: https://vsoch.github.io/2018/django-nginx-upload/

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
