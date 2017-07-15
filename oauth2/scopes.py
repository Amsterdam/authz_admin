"""Interface to the datasets and scopes defined in the configuration file.

The configuration file defines a number of *datasets*, and each dataset has a
number of *scopes*. *Datasets* have a unique identifier consisting of 1–4
alphanumeric characters.

"""

import functools

from oauth2 import config


# New stuff from Pieter


@functools.lru_cache()
def all_scopes():
    # language=rst
    """All scopes defined in the configuration.

    :rtype: frozenset(str)

    """
    retval = []
    for dataset_token, dataset in config.get().get('datasets', {}).items():
        for scope_token in dataset.get('scopes', {}):
            retval.append("{}.{}".format(dataset_token, scope_token))
    return frozenset(retval)
