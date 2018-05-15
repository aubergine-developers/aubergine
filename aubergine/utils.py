"""Utility functions used in aubergine."""
from collections import Callable
import logging
import importlib
from aubergine.handlers import RequestHandler


def create_resource(handlers):
    """Combine request handlers into a resource that can be used with Falcon.

    :param handlers: map: method -> request handler used for forming a Resource.
    :type handlers: mapping: str -> :py:class:`aubergine.RequestHandler`
    :returns: An object having on_<methond> methods, where <method> runs over all
     keys in `handlers` mapping (lowercased). Those methods are bound to `handle_request`
     of corresponding `RequestHandler`.
    :rtype: runtime created type with the name 'Resource<path>` where path is equal
     to first handler `path` attribute (it is silently assumed that all handlers were
     constructed for the same path)
    """
    path = next(iter(handlers.values())).path
    attrs = {'on_' + meth.lower(): handler.handle_request for meth, handler in handlers.items()}
    cls = type('Resource<{}>'.format(path), tuple(), attrs)
    return cls()


def create_handler(path, op_spec, extractor_factory, import_module=importlib.import_module):
    """Create handler from given specification."""
    logger = logging.getLogger('create_handler')

    if 'requestBody' in op_spec:
        body_ex = extractor_factory.build_body_extractor(op_spec['requestBody'])
    else:
        body_ex = None

    param_ex = {}
    for param in op_spec.get('parameters', tuple()):
        param_ex[param['name']] = extractor_factory.build_param_extractor(param)

    op_id = op_spec['operationId']
    dot_idx = op_spec['operationId'].rfind('.')
    if dot_idx == -1:
        logger.error('Cannot split operationId into module/package and attr part.')
        raise ValueError(op_spec['operationId'])
    module = import_module(op_id[:dot_idx])
    operation = getattr(module, op_id[dot_idx+1:])
    if not isinstance(operation, Callable):
        logger.error('Object %s is not callable, it cannot serve as an operation.', op_id)
        raise TypeError(op_id)

    return RequestHandler(path=path,
                          operation=operation,
                          body_extractor=body_ex,
                          params_extractors=param_ex)
