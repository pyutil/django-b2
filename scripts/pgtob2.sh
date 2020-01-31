#!/usr/bin/env bash

# make ~/.pgpass with row: localhost:5432:<dbname>:<dbuser>:<password>
# then call: pgtob2.sh dbname dbuser envfile envfilesection path-to-this-package
#   dbname                database to backup
#   dbuser                database user with access to this database (maybe you name it identically)
#   envfile               full pathname of .ini file (which can but need not be shared with your django app,
#                         if so other b2 credentials, SECRET_KEY,.. can be present; but maybe you use different
#                         scenario (like environment variables) or you simply prefer not use the shared file)
#   envfilesection        the section in .ini file; example: if set to: bk, the .ini file should contain:
#                             [bk]
#                             B2_APP_KEY_ID=000xxxxxxxxxxxx000000000n
#                             B2_APP_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#                             B2_BUCKET_NAME=bucketname
#   path-to-this-package  path to django_b2/ include trailing / ; django_b2/backblaze_b2.py will be immediately appended

# you may want a cron task; this can be root's crontab; example:
# crontab -e
# 0 3 * * * /home/www-data/.virtualenvs/myapp/bin/pgtob2.sh/pgtob2.sh mydb mydb-user /etc/django/myapp.ini bk /home/www-data/.virtualenvs/myapp/lib/python3.7/site-packages/

# For ~/.pgpass and <envfile> we need limit the read access to users who need it.
# For ~/.pgpass this is the user who runs this backup (cron backup), lets say in production you run this as root. So:
#   ~ is the root's homedir, then:
#   chmod 0600 ~/.pgpass
#   chown root:root ~/.pgpass
# For <envfile> cron must have access (with regard to this backup) but if you share some settings the django app user
#       (usually www-data) need access too. So:
#   chmod 0600 <envfile>
#   chown www-data:www-data <envfile>   # the <envfile> will still be read-accessible by root (needed in cron backup)
# Maybe you set the owners/rights/.. differently. If so you should find a good way for your scenario.

pg_dump -Fc -d $1 -U $2 > pg_dump_$1.dump
# pg_restore -d $1 pg_dump_$1.dump

python3 $5django_b2/backblaze_b2.py pg_dump_$1.dump -e $3 -s $4
