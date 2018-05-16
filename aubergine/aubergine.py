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


    def __init__(self, spec_dict):
        self.spec_dict = spec_dict

    def build_api(self, api_factory=falcon.API, **kwargs):
        logger = logging.getLogger('aubergine')
        self._greet()
        logger.info('Buidling app %s (version %s)',
                    self.spec_dict['info']['title'] ,
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
