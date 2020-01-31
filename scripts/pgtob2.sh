#!/usr/bin/env bash

# ~/.pgpass: localhost:5432:<dbname>:<dbuser>:<password>
# ./pgtob2.sh dbname dbuser envfile envfilesection

# ve run as normal user (to have access to python virtualenv) and so we set for both ~/.pgpass and <envfile>:
#   chmod 0600 <filename>
#   chown normaluser:normaluser <filename>

# crontab -e
# 0 3 * * * scripts/pgtob2.sh mydb mydb-user /etc/xxx/xxx/xxx.ini bk

pg_dump -Fc -d $1 -U $2 > pg_dump_$1.dump
# pg_restore -d $1 pg_dump_$1.dump

python django_b2/backblaze_b2.py pg_dump_$1.dump -e $3 -s $4
