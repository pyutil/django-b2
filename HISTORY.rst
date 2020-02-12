.. :changelog:

History
-------

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
