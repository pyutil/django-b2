from io import BytesIO

from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import File
from django.utils.deconstruct import deconstructible

from .backblaze_b2 import BackBlazeB2


# B2File related imports, TODO: mix with non-experimental imports if B2File will be used
from shutil import copyfileobj
from tempfile import SpooledTemporaryFile


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
        application_key_id = settings.BACKBLAZEB2_APP_KEY_ID
        application_key = settings.BACKBLAZEB2_APP_KEY
        bucket_id = settings.BACKBLAZEB2_BUCKET_NAME

        self.b2 = BackBlazeB2()
        self.authorize(application_key_id, application_key)
        self.set_bucket(bucket_id)

    # you can re-authorize later
    def authorize(self, application_key_id, application_key):
        return self.b2.authorize("production", application_key_id, application_key)

    # you can change bucket later
    def set_bucket(self, bucket_id):
        return self.b2.set_bucket(bucket_id)

    # ------------- django Storage extension --------------

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

        # this is based on django-storage:DropBox
        # TODO: this works, but need revision and rewrite, please help!
        download_dest = self.b2.download_file_download_dest(name)
        return B2File(name, download_dest)

    def _save(self, name, content, max_length=None):
        response = self.b2.upload_file_unique_name(name, content)
        return response.file_name

    def delete(self, name):
        return self.b2.delete_by_name(name)

    # maybe expensive
    def listdir(self, path):
        if len(path) and path[-1] != '/':
            path += '/'
        dirs = set()
        files = []
        for file_info, file_path in self.b2.ls(path):
            if file_path is None:
                files.append(file_info.file_name.rsplit('/', 1)[-1])
            else:
                file_path = file_path[len(path):]
                dirs.add(file_path.split('/', 1)[0])
        return list(dirs), files

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
