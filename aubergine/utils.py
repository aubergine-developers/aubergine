"""Utility functions used in aubergine."""


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
