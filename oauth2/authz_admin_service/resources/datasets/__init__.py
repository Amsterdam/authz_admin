from oauth2.authz_admin_service import resource_types

from . import dataset

resource = resource_types.Collection('/datasets/', name='datasets')

