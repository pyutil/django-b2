# except of its standard usage this can be used as the copy/upload command to backblaze
#   for help write: python backblaze_b2 --help
#   warning: additional imports for this usage are in 'command' section bellow

from datetime import datetime
import uuid

from b2sdk.v1 import B2Api, DownloadDestBytes, InMemoryAccountInfo, UploadSourceBytes

try:
    from django.utils import timezone
    USE_TZ = True
except (ModuleNotFoundError, ImportError) as exc:
    USE_TZ = False


LS_FETCH_COUNT = 1000    # probably 100 is default, 1000-10000 are paid based on 1000-chunks
DOWNLOAD_TIMEOUT = 1800  # validity of download links [s]


class BackBlazeB2(object):
    def __init__(self):
        info = InMemoryAccountInfo()
        self.b2_api = B2Api(info)

        self.bucket = None
        self.authorized = False

    # need to call this after instantiate; you could change this later
    def authorize(self, name, application_key_id, application_key):
        # name: usually can be: "production"
        self.b2_api.authorize_account(name, application_key_id, application_key)
        self.authorized = True

    # need to call this after instantiate; you could change this later
    def set_bucket(self, bucket_name):
        self.bucket = self.b2_api.get_bucket_by_name(bucket_name)

    def is_prepared(self):   # was .authorize and .set_bucket called earlier?
        return self.authorized and self.bucket is not None

    # ------------------------------------------------------------------

    def download_file(self, name):                 # return DownloadDestBytes() str content
        return self.download_file_download_dest(name).get_bytes_written()

    def download_file_download_dest(self, name):   # return DownloadDestBytes() object
        assert self.is_prepared()
        download_dest = DownloadDestBytes()
        self.bucket.download_file_by_name(name, download_dest)
        return download_dest

    def upload_file(self, name, f):
        assert self.is_prepared()
        content = f.read()
        if 'b' not in f.mode:
            content = content.encode()
        uploadsource = UploadSourceBytes(content)
        return self.bucket.upload(uploadsource, name)

    def upload_file_unique_name_outside_django(self, name, f):
        """
            django storage auto-calls get_alternative_name() so from django call upload_file() directly
        """
        return self.upload_file(self.get_alternative_name(name), f)

    def delete_by_name(self, name):
        for version in self.versions_by_name(name):
            self.delete_file_version(name, version['fileId'])

    def delete_file_version(self, name, file_id):
        assert self.is_prepared()
        return self.bucket.delete_file_version(file_id, name)

    # maybe expensive
    def purge_bucket(self):
        # purge large uncommitted uploads is not implemented here
        while True:
            versions = self._list_versions()
            for version in versions['files']:
                self.delete_file_version(version['fileName'], version['fileId'])
            if versions['nextFileId'] is None:
                break

    def get_file_info(self, file_id):
        assert self.is_prepared()
        return self.b2_api.get_file_info(file_id)

    def get_file_info_by_name(self, name):
        assert self.is_prepared()
        file_id = self.file_id_by_name(name)
        return self.get_file_info(file_id)

    def get_download_url(self, name):
        assert self.is_prepared()
        url = self.bucket.get_download_url(name)   # == self.b2.get_file_url(name)
        if 'private' in self.bucket.bucket_dict['bucketType'].lower():
            url += '?Authorization=' + self.bucket.get_download_authorization(name,
                                                                            valid_duration_in_seconds=DOWNLOAD_TIMEOUT)
        return url

    # maybe expensive
    def ls(self, path, fetch_count=LS_FETCH_COUNT):
        assert self.is_prepared()
        # this is generator (which handles chunks, so it returns all entries & fetch_count has an internal effect only)
        return self.bucket.ls(folder_to_list=path, fetch_count=fetch_count)

    # maybe expensive
    def listdir(self, path):
        """
            :return: compatible with Django storage : listdir
        """
        if len(path) and path[-1] != '/':
            path += '/'
        dirs = set()
        files = []
        for file_info, file_path in self.ls(path):
            if file_path is None:
                files.append(file_info.file_name.rsplit('/', 1)[-1])
            else:
                file_path = file_path[len(path):]
                dirs.add(file_path.split('/', 1)[0])
        return list(dirs), files

    def file_by_name(self, name):
        # is there a less stupid way to do it?
        assert self.is_prepared()
        fn = self.b2_api.raw_api.list_file_names(self.b2_api.account_info.get_api_url(),
                                                 self.b2_api.account_info.get_account_auth_token(),
                                                 self.bucket.get_id(),
                                                 start_file_name=name, max_file_count=1, prefix=name)
        return self._x_by_name_result(fn, name)

    def versions_by_name(self, name):
        # is there a less stupid way to do it?
        fn = self._list_versions(name)
        return self._x_by_name_result(fn, name)

    def _list_versions(self, name=None, start_file_name=None, start_file_id=None):
        # returns at most 1000 file names per transaction
        assert self.is_prepared()
        if name:
            start_file_name = name
            kwargs = {'prefix': name}
        else:
            kwargs = {}
        retval = self.b2_api.raw_api.list_file_versions(self.b2_api.account_info.get_api_url(),
                                                        self.b2_api.account_info.get_account_auth_token(),
                                                        self.bucket.get_id(),
                                                        start_file_name=start_file_name,
                                                        start_file_id=start_file_id,
                                                        max_file_count=LS_FETCH_COUNT,
                                                        **kwargs)
        if type(retval) == dict:
            return retval
        else:
            return {'files': []}  # seems at 2020-01-06 b2_api returns str:'files', which is probably a minor bug

    def _x_by_name_result(self, fn, name):
        res = []
        for f in fn['files']:
            if f['fileName'] == name:
                res.append(f)
        return res

    def file_id_by_name(self, name):
        # is there a less stupid way to do it?
        f = self.file_by_name(name)
        if len(f) == 0:
            return None
        else:
            return f[0]['fileId']

    def get_accessed_time(self, name, use_tz=USE_TZ):  # we haven't accessed time, so..
        return self.get_modified_time(name, use_tz)        # TODO: isn't NotImplemented better?

    def get_created_time(self, name, use_tz=USE_TZ):
        assert self.is_prepared()
        versions = self.versions_by_name(name)
        return self._get_time_from_fileinfo(versions, use_tz)

    def get_modified_time(self, name, use_tz=USE_TZ):
        assert self.is_prepared()
        f = self.file_by_name(name)
        return self._get_time_from_fileinfo(f, use_tz)

    @staticmethod
    def _get_time_from_fileinfo(fileinfo, use_tz):
        if not fileinfo:
            return None
        ts = int(fileinfo[-1]['uploadTimestamp'] / 1000)
        if use_tz:
            return datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc)
        else:
            return datetime.fromtimestamp(ts)

    # named compatible with Django 3.0
    def get_alternative_name(self, name):
        name = name.split('/')
        name.insert(len(name) - 1, str(uuid.uuid4()))
        return '/'.join(name)

    def get_original_name(self, name):
        return get_original_name(name)


# ------- utils, can be imported separately -----------------------


# revert get_alternative_name()
def get_original_name(name):
    name = name.split('/')
    if len(name) > 1:
        del name[-2]
    return '/'.join(name)


# ------- commands -----------------------

if __name__ == '__main__':   # upload file to backblaze
    # additional imports
    import os
    import sys
    from configparser import RawConfigParser
    # parse commandline
    cp_argv = sys.argv
    cp_filename = cp_argv[1:2]
    cp_envfile = cp_argv[2:3]
    cp_section = cp_argv[3:4]
    cp_b2path = cp_argv[4:5] or ''
    if ('-h' not in cp_argv[1:] and '--help' not in cp_argv[1:] and
        cp_filename and cp_envfile and cp_section and os.path.isfile(cp_filename) and os.path.isfile(cp_envfile)):
        # doit !
        config = RawConfigParser()
        config.read(cp_envfile)

        cp_b2 = BackBlazeB2()
        cp_b2.authorize("production", application_key_id, application_key)
        cp_b2.set_bucket(self, bucket_name)

        with open(cp_filename, 'rb') as f:
            cp_b2.upload_file(name, f)
    else:
        # print help
        print()
        print('Copy/upload file to b2: python backblaze_b2 filename envfile section [b2path]')
        print()
        print(4 * ' ' + 'filename  file to be uploaded')
        print(4 * ' ' + 'envfile   .ini style file with backblaze settings')
        print(4 * ' ' + 'section   section name in <envfile>, the section must contain:')
        print(8 * ' ' + 'B2_APP_KEY_ID=000xxxxxxxxxxxx000000000n')
        print(8 * ' ' + 'B2_APP_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        print(8 * ' ' + 'B2_BUCKET_NAME=bucketname')
        print(4 * ' ' + 'b2path    optional path in the target bucket')
        print()
