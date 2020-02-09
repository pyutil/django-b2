import argparse
from datetime import datetime, timedelta
import logging
import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured

from django_b2.storage import B2Storage, LOGFILE_PREFIX, META_LOCATION


HISTORY_LOCATION = 'history/'


log = logging.getLogger('avis')


class Command(BaseCommand):
    help = ("Delete local media (copy of backblaze upload) and copy log to <MEDIA_ROOT>/%s/%s. "
           "This can be used together with the B2_LOCAL_CACHE='FM' setting." % (META_LOCATION, HISTORY_LOCATION))

    def add_arguments(self, parser):
        def positive_type(x):
            x = int(x)
            if x < 1:
                raise argparse.ArgumentTypeError("Minimum for --days or --hours is 1.")
            return x

        parser.add_argument('--days', type=positive_type,
                            help="Delete local media older than N days. """
                                 "Default is 1 day used if both --days and --hours are missing")
        parser.add_argument('--hours', type=positive_type)
        parser.add_argument('--no-history', action='store_true',
                            help="Do not backup solved meta (log) files to <MEDIA_ROOT>/%s/%s"
                            % (META_LOCATION, HISTORY_LOCATION))

    def handle(self, *args, **options):
        if not settings.MEDIA_ROOT:
            raise ImproperlyConfigured("Cannot seek for local media files, MEDIA_ROOT isn't set.")
        meta_dir = os.path.join(settings.MEDIA_ROOT, META_LOCATION)
        if not os.path.isdir(meta_dir):
            raise ImproperlyConfigured("Cannot seek for local media files, MEDIA_ROOT isn't set.")

        hours = options.get('hours', 0)
        if options['days']:
            hours += 24 * options['days']
        elif not hours:
            hours = 24  # default is 1 day
        self.handle_clean(hours, meta_dir, no_history=options['no_history'])

    def handle_clean(self, hours, meta_dir, no_history=False):
        bk_dir = None
        if not no_history:
            bk_dir = os.path.join(meta_dir, HISTORY_LOCATION)
            os.makedirs(bk_dir, exist_ok=True)
        max_filename = self.get_max_filename(hours)
        for log_file in os.listdir(meta_dir):
            if log_file.startswith(LOGFILE_PREFIX) and log_file <= max_filename:
                log_full = os.path.join(meta_dir, log_file)
                if os.path.isfile(log_full):  # directories, like history/ shouldn't start with LOGFILE_PREFIX, but..
                    log_ok = self.handle_clean_logfile(log_full)
                    if log_ok:
                        if bk_dir is None:
                            os.remove(log_full)
                        else:
                            shutil.move(log_full, os.path.join(bk_dir, log_file))  # move log file to history/

    def handle_clean_logfile(self, log_full):
        log_ok = True
        with open(log_full, 'r') as f:
            media_files = f.readlines()
            for media_file in media_files:
                if media_file:
                    media_file = os.path.join(settings.MEDIA_ROOT, media_file)
                    if os.path.isfile(media_file):
                        try:
                            os.remove(media_file)
                        except Exception:
                            log_ok = False
        return log_ok

    def get_max_filename(self, hours):
        assert hours >= 1, "Expected to delete 1+ hours old media files, but hours < 1; stopping, to be safe."
        return B2Storage.get_logfile_name(datetime.now() - timedelta(hours=hours + 1))  # N hours -> interval(N, N+1)
