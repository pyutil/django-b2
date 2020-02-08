.. :changelog:

History
-------

0.3.0 (2020-02-08)
++++++++++++++++++

* B2_LOCAL_CACHE setting to make a local copy of files. So you can have local instances backuped on backblaze.
* B2_LOCAL_CACHE prevents failures if the django application want immediately reopen the file (imagekits creating thumbnails, Wagtail is an example)

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
