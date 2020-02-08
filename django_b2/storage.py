"""
    B2Storage
        uses b2sdk

    add this to your Django settings:
        DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'
        B2_APP_KEY_ID = '000xxxxxxxxxxxx000000000n'
        B2_APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        B2_BUCKET_NAME = '<bucket-name>'

    this storage makes names unique by change path/name into path/<uuid>/name
        so it is not compatible with storage uploaded using django-backblazeb2-storage
            where files with same names are uploaded without name change and as versions of same file

    behaviour of exceptions (FileNotFoundError, NotADirectoryError, ..) is not fully compatible

    methods _open, _save works but need experienced revision and rewrite (please help)
"""


from io import BytesIO
import os
from datetime import datetime

from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.core.files.base import ContentFile, File
from django.utils.deconstruct import deconstructible

from django_b2.backblaze_b2 import BackBlazeB2


# B2File related imports, TODO: mix with non-experimental imports if B2File will be used
from shutil import copyfileobj
from tempfile import SpooledTemporaryFile


# if 'M' in settings.B2_LOCAL_CACHE, list of uploaded files will be created in MEDIA_ROOT/<META_LOCATION>
META_LOCATION = '_meta'


# experimental (B2File class, B2Storage._open), inspired from django-storages DropBoxFile
# TODO: this works, but need revision and rewrite, please help!
@deconstructible
class B2File(File):
    def __init__(self, name, download_dest):
        self.name = name
        self._download_dest = download_dest
        self._file = None

    def _get_file(self):
        if self._file is None:
            self._file = SpooledTemporaryFile()
            with BytesIO(self._download_dest.get_bytes_written()) as file_content:
                copyfileobj(file_content, self._file)
            self._file.seek(0)
            # self._download_dest = None
        return self._file

    def _set_file(self, value):
        self._file = value

    file = property(_get_file, _set_file)


@deconstructible
class B2Storage(Storage):
    def __init__(self):
        application_key_id = settings.B2_APP_KEY_ID
        application_key = settings.B2_APP_KEY
        bucket_name = settings.B2_BUCKET_NAME

        self.b2 = BackBlazeB2()
        self.authorize(application_key_id, application_key)
        self.set_bucket(bucket_name)

        self.fs = self.meta = None
        if hasattr(settings, 'B2_LOCAL_CACHE'):
            assert settings.MEDIA_ROOT, 'B2_LOCAL_CACHE used. Please set MEDIA_ROOT in your settings.'
            if 'F' in settings.B2_LOCAL_CACHE:
                self.fs = FileSystemStorage()
            if 'M' in settings.B2_LOCAL_CACHE:
                self.meta = os.path.join(settings.MEDIA_ROOT, META_LOCATION)
                os.makedirs(self.meta, exist_ok=True)

    # you can re-authorize later
    def authorize(self, application_key_id, application_key):
        return self.b2.authorize("production", application_key_id, application_key)

    # you can change bucket later
    def set_bucket(self, bucket_name):
        return self.b2.set_bucket(bucket_name)

    # ------------- django Storage extension --------------

    # method added with regard to Django 3.0 compatibility, both (available/alternative) do the same: add <uuid>/
    def get_alternative_name(self, file_root, file_ext=''):
        name = '%s%s' % (file_root, file_ext)
        return self.b2.get_alternative_name(name)

    # both (available/alternative) do the same: add <uuid>/
    # important to have this: to prevent inefficient .exists() call
    def get_available_name(self, name, max_length=None):
        return self.b2.get_alternative_name(name)

    def _open(self, name, mode='rb'):
        '''
        # this is based on django-backblazeb2-storage
        # TODO: this works, but need revision and rewrite, please help!
        resp = self.b2.download_file(name)
        output = BytesIO()
        output.write(resp)
        output.seek(0)
        return File(output, name)
        '''
        if self.fs is not None and os.path.isfile(os.path.join(settings.MEDIA_ROOT, name)):
            return self.fs._open(name)
        else:
            # this is based on django-storage:DropBox
            # TODO: this works, but need revision and rewrite, please help!
            download_dest = self.b2.download_file_download_dest(name)
            return B2File(name, download_dest)

    def _save(self, name, f, max_length=None):
        if self.fs is not None:
            self.fs.save(name, ContentFile(f.read()))
            f.seek(0)
        if self.meta is not None:
            metafile = os.path.join(self.meta, 'uplooad_' + datetime.now().isoformat()[:13])
            with open(metafile, 'a') as mf:
                mf.writelines([name + '\n'])
        response = self.b2.upload_file(name, f)
        return response.file_name

    def delete(self, name):
        return self.b2.delete_by_name(name)

    # maybe expensive
    def listdir(self, path):
        return self.b2.listdir(path)

    def exists(self, name):
        return self.b2.file_id_by_name(name) is not None

    def size(self, name):
        return self.b2.get_file_info_by_name(name)['contentLength']

    def url(self, name):
        return self.b2.get_download_url(name)

    def path(self, name):
        # This is needed because Django will throw an exception if it's not
        # overridden by Storage subclasses. We don't need it.
        return name
        # TODO: maybe this can be used to avoid some downloads / cache files locally?
        '''
        """
        Return a local filesystem path where the file can be retrieved using
        Python's built-in open() function. Storage systems that can't be
        accessed using open() should *not* implement this method.
        """
        raise NotImplementedError("This backend doesn't support absolute paths.")
        '''

    def get_accessed_time(self, name):
        return self.b2.get_accessed_time(name, use_tz=settings.USE_TZ)

    def get_created_time(self, name):
        return self.b2.get_created_time(name, use_tz=settings.USE_TZ)

    def get_modified_time(self, name):
        return self.b2.get_modified_time(name, use_tz=settings.USE_TZ)
