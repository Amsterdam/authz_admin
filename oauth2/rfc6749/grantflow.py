"""
"""
import collections
import enum

from . import exceptions

Flow = collections.namedtuple('Flow', 'response_type responseclass')


class GrantFlow(enum.Enum):

    AUTHORIZATION_CODE = Flow(response_type='code', responseclass=None)
    IMPLICIT = Flow(response_type='token', responseclass=None)

    @classmethod
    def for_response_type(cls, response_type):
        for flow_type in cls:
            if flow_type.response_type == response_type:
                return flow_type
        raise exceptions.UnknownResponseTypeError()
