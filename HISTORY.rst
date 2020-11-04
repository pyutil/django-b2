.. :changelog:

History
-------

0.6.2 (2020-11-04)
++++++++++++++++++

* B2Storage() initializes as the settings.DEFAULT_FILE_STORAGE if 'B2Storage' string is not inside
  can be used together with @override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
  see https://github.com/pyutil/django-b2/issues/4

0.6.0 (2020-05-28)
++++++++++++++++++

* lazy loading, to avoid running code during collectstatic,.. - https://github.com/pyutil/django-b2/issues/3

0.5.5 (2020-05-24)
++++++++++++++++++

* bugfix: upload on Windows, thx Same Weaver, https://github.com/pyutil/django-b2/issues/2
* Linux abs filenames: leading "/" will be removed so we can use local abs names 1:1 to upload to b2 (in Windows: C:/.. is valid name)

0.5.0 (2020-02-17)
++++++++++++++++++

* can work with django-tenant schemas, tenant aware storage django_b2.tenant_storage.TenantB2Storage

0.4.0 (2020-02-10)
++++++++++++++++++

* older local media (see B2_LOCAL_MEDIA) can be cleared with management command b2_clear_local_media
* B2_LOCAL_CACHE setting renamed to B2_LOCAL_MEDIA, possible values changed to ="ML"

0.3.0 (2020-02-08) - do not use
+++++++++++++++++++++++++++++++

* !! new B2_LOCAL_MEDIA setting was in 0.3.0 named incompatible as B2_LOCAL_CACHE="FM"
* B2_LOCAL_MEDIA setting to make a local copy of files. So you can have local instances backuped on backblaze.
* B2_LOCAL_MEDIA prevents failures if the django application want immediately reopen the file (imagekits creating thumbnails, Wagtail is an example)

0.2.0 (2020-01-31)
++++++++++++++++++

* backblaze_b2.py can be called as script to upload single file.
* pgtob2.sh script to backup postgres database

0.1.5 (2020-01-02)
++++++++++++++++++

* No code change. Minor docs changes.

0.1.4 (2020-01-02)
++++++++++++++++++

* First release on PyPI.
