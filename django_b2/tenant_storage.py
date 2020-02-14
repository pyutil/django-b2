# Tenant aware storages
# Can be used together with postgres and django-tenant-schemas

# https://github.com/bernardopires/django-tenant-schemas/issues/565

from tenant_schemas.storage import TenantStorageMixin

# original: DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'
from django_b2.storage import B2Storage


# DEFAULT_FILE_STORAGE = 'django_b2.tenant_storage.TenantB2Storage'
class TenantB2Storage(TenantStorageMixin, B2Storage):
    pass
