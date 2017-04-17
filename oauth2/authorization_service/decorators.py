"""
"""
import functools

from oauth2 import clientregistry
from oauth2.rfc6749 import AuthorizationRequest


def authorizationrequest(*supported_flows):
    """ Returns a decorator that can be used to turn a view into one that
    supports an OAuth2 authorization request.

    :param supported_flows: the flows that this view supports (token, code, ..)
    """
    def decorator(f):
        """ Any view function decorated with this decorator will be called with
        an AuthorizationRequest instance as its single argument.
        """
        @functools.wraps(f)
        def wrapper(request):
            request.__class__ = AuthorizationRequest
            request.supported_response_types = [*supported_flows]
            request.clientregistry = clientregistry
            return f(request)
        return wrapper
    return decorator
