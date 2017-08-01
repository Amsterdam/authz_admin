import typing as T
import abc

import rest_utils


class OAuth2View(rest_utils.View, metaclass=abc.ABCMeta):
    """Default Query Parameters Mixin."""

    @property
    def default_query_params(self: rest_utils.View) -> T.Dict[str, str]:
        """

        See :func:`rest_utils.View.default_query_params`.

        """
        path, path_info = self.request.app['swagger'].get_path_spec(
            self.rel_url.raw_path,
            action=self.request.method.lower()
        )
        if path is None:
            return {}
        return dict({
            param: param_info['default']
            for param, param_info in path_info.get('parameters', {}).items()
            if 'default' in param_info
        })

    async def attributes(self):
        swagger = self.request.app['swagger']
        _, path_spec = swagger.get_path_spec(self.rel_url.raw_path)
        return {
            'swagger': path_spec
        }

    @property
    @abc.abstractmethod
    def title(self) -> str:
        pass

    @property
    def to_link(self):
        result = super().to_link
        result['title'] = self.title
        return result
