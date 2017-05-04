"""
    oauth2.userregistry
    ~~~~~~~~~~~~~~~~~~~

    Placeholder for the user registry. The user registry maps user identifiers
    onto user attributes, e.g. scopes.
"""
import collections

User = collections.namedtuple('User', 'uid idp_id scopes')

_registry = (
    User(
        uid='datapunt.ois@amsterdam.nl',
        idp_id='testidp',
        scopes={'default', 'employee', 'employee_plus'}
    ),
)


class _Registry(collections.abc.Mapping):

    __len__ = _registry.__len__

    def __getitem__(self, key):
        """ Get user information from the registry based on a user id
        """
        result = tuple(c for c in _registry if c.uid == key)
        if len(result) == 0:
            raise KeyError('Unknown user id')
        return result[0]

    def __iter__(self):
        for c in _registry:
            yield c.uid


instance = _Registry()


def get():
    return instance
