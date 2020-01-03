# add this to your settings:

# DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'
# BACKBLAZEB2_APP_KEY_ID = '000xxxxxxxxxxxx000000000n'
# BACKBLAZEB2_APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# BACKBLAZEB2_BUCKET_NAME = '<bucket-name>'


import uuid

from b2sdk.v1 import B2Api, DownloadDestBytes, InMemoryAccountInfo, UploadSourceBytes


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
        self.b2_api.authorize_account(name, application_key_id, application_key)
        self.authorized = True

    # need to call this after instantiate; you could change this later
    def set_bucket(self, bucket_name):
        self.bucket = self.b2_api.get_bucket_by_name(bucket_name)

    def is_prepared(self):   # was .authorize and .set_bucket called earlier?
        return self.authorized and self.bucket is not None

    # ------------------------------------------------------------------

    def download_file(self, name):                 # return DownloadDestBytes() str content
        return download_file_download_dest(name).get_bytes_written()

    def download_file_download_dest(self, name):   # return DownloadDestBytes() object
        assert self.is_prepared()
        download_dest = DownloadDestBytes()
        self.bucket.download_file_by_name(name, download_dest)
        return download_dest

    def upload_file(self, name, content):
        assert self.is_prepared()
        uploadsource = UploadSourceBytes(content.read())
        return self.bucket.upload(uploadsource, name)

    def upload_file_unique_name(self, name, content):
        return self.upload_file(make_name_unique(name), content)

    def delete_by_name(self, name):
        for version in self.versions_by_name(name):
            self.delete_file_version(name, version['fileId'])

    def delete_file_version(self, name, file_id):
        assert self.is_prepared()
        return self.bucket.delete_file_version(file_id, name)

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
        # this is generator;
        assert self.is_prepared()
        return self.bucket.ls(folder_to_list=path, fetch_count=fetch_count)

    def versions_by_name(self, name):
        # is there a less stupid way to do it?
        assert self.is_prepared()
        fn = self.b2_api.raw_api.list_file_names(self.b2_api.account_info.get_api_url(),
                                                 self.b2_api.account_info.get_account_auth_token(),
                                                 self.bucket.get_id(),
                                                 start_file_name=name, max_file_count=1, prefix=name)
        versions = []
        for f in fn['files']:
            if f['fileName'] == name:
                versions.append(f)
        return versions

    def file_id_by_name(self, name):
        # is there a less stupid way to do it?
        versions = self.versions_by_name(name)
        if len(versions) == 0:
            return None
        else:
            return versions[0]['fileId']


# ----------------------- utils -----------------------


def make_name_unique(name):
    name = name.split('/')
    name.insert(len(name) - 1, str(uuid.uuid4()))
    return '/'.join(name)


def get_original_name(name):
    name = name.split('/')
    if len(name) > 1:
        del name[-2]
    return '/'.join(name)
