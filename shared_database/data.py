"""
This module contains semi-dynamic data.

:data:`IDENTITY_PROVIDERS` contains a dict of all supported Identity Providers,
indexed by unique id (an integer >= 1).

:data:`DATASETS` contains a dict of all datasets that we administer permissions for,
indexed by unique id (an integer >= 1).

"""

from collections import namedtuple


######################
# IDENTITY PROVIDERS #
######################

_IdentityProvider = namedtuple('IdentityProvider', ('name',))

IDENTITY_PROVIDERS = {
    1: _IdentityProvider(
        name="Toegangsmakelaar Amsterdam"
    )
}

############
# DATASETS #
############

_Dataset = namedtuple('Dataset', ('name',))

DATASETS = {
    1: _Dataset("Basisadministratie Gebouwen"),
    2: _Dataset("Handelsregister")
}


if __name__ == '__main__':
    print(IDENTITY_PROVIDERS)

