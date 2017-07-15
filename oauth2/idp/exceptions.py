"""
    oauth2.idp.exceptions
    ~~~~~~~~~~~~~~~~~~~~~
"""


class FailedAuthentication(Exception):
    # language=rst
    """ Exception that should be raised when an IdP concludes that for whatever
    reason, authentication has failed. Raising this error will result in a
    401 Unauthorized response.
    """
