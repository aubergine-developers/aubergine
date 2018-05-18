"""Definition of main class - aubergine's public API."""
import importlib
import logging
from urllib.parse import urlparse
import falcon
from nadia.api import SchemaBuilder
import ymlref
from aubergine.extractors import ExtractorBuilder
from aubergine import utils


class Aubergine:
    """Main class for declaring an application.

    :param spec_dict: mapping defining OpeanAPI spefication.
    :type spec_dict: Mapping
    """

    def __init__(self, spec_dict):
        self.spec_dict = spec_dict

    def build_api(self, api_factory=falcon.API, **kwargs):
        """Build falcon API for this aubergine app.

        :param api_factory: a callable to obtain API instance from. Defaults to
         :py:class:`falcon.API`. Can be usefull if you wish to precreate API
          yourself (and for instance manipulate it somehow before it gets
          processed by Aubergine.
        :type api_factory: Callable
        :param kwargs: keyword arguments that can control api's creation. Usually
         not needed but here's the list of used `kwargs` anyway:
         -  'ex_factory': a :py:class:`aubergine.extractors.ExtractorBuilder` instance.
            If not provided, one will be created for you.
         - 'import_module': a callable that can be used to load modules/operations.
           More generally, it is a callable that will be called for every operation
           with argument being the part of operationId before the last dot. It should
           return any object with attribute matching part of operationId after the dot.
           For instance, for 'my.package.oper' operationId, import_module will be
           called with 'my.package' argument, and is supposed to return anything with
           `oper` atrribute (callable with argument matching the appropriate operation
           schema. Defaults to :py:func:`importlib.import_module`
        :returns: an API object
        :rtype: :py:class:`falcon.API`
        """

        logger = logging.getLogger('aubergine')
        self._greet()
        logger.info('Buidling app %s (version %s)',
                    self.spec_dict['info']['title'],
                    self.spec_dict['info']['version'])
        ex_factory = kwargs.get('ex_factory', ExtractorBuilder(SchemaBuilder.create()))
        import_module = kwargs.get('import_module', importlib.import_module)
        base_path = self._get_base_path()
        logger.info('Using base path %s', base_path)
        api = api_factory()
        for path, path_spec in self.spec_dict['paths'].items():
            logger.info('Creating handlers for path %s', path)
            handlers = {meth: utils.create_handler(path, op_spec, ex_factory, import_module)
                        for meth, op_spec in path_spec.items()}
            resource = utils.create_resource(handlers)
            api.add_route('/'.join((base_path.rstrip('/'), path.strip('/'))), resource)
        return api

    @classmethod
    def from_file(cls, path):
        """Shorthand for loading spec from given path and constructing Aubergine from it."""
        with open(path) as specfile:
            content = specfile.read()
            return cls(ymlref.load(content))

    def _get_base_path(self):
        base_paths = {urlparse(server['url']).path for server in self.spec_dict['servers']}
        if len(base_paths) != 1:
            raise ValueError("Base paths of servers differ, I don't know which one to use.")
        return next(iter(base_paths))

    def _greet(self):
        print(self.LOGO)

    LOGO = """
 █████╗ ██╗   ██╗██████╗ ███████╗██████╗  ██████╗ ██╗███╗   ██╗███████╗
██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗██╔════╝ ██║████╗  ██║██╔════╝
███████║██║   ██║██████╔╝█████╗  ██████╔╝██║  ███╗██║██╔██╗ ██║█████╗
██╔══██║██║   ██║██╔══██╗██╔══╝  ██╔══██╗██║   ██║██║██║╚██╗██║██╔══╝
██║  ██║╚██████╔╝██████╔╝███████╗██║  ██║╚██████╔╝██║██║ ╚████║███████╗
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝╚══════╝
                                                                       """
