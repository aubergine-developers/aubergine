from collections import Callable
import importlib

class InvalidOperationPathError(ValueError):
    """An error raised when operation path to load is not correct syntactically."""


class NotCallableError(ValueError):
    """An error raised when loaded object is not callable and cannot be an operation."""


class OperationLoader:
    """Class for loading operations given their id."""

    def __init__(self, import_module=importlib.import_module):
        self.import_module = import_module

    def load(self, path):
        """Load operation from given path.

        The operatoinId in OpenAPI spec used by aubergine is assumed to be a path to
        the callable e.g. `mypackage.mymodule.my_func`.
        Therefore mypackage.mymodule should be importable and contain my_func
        attribute.

        :param path: path of the operation, e.g mypackage.mymodule.foo
        :type path: str
        :returns: operation loaded from the given path
        :rtype: type of mypackage.mymodule.my_func
        :raises InvalidOperationPathError: if path does not contain dot (and
         therefore it is impossible to distinguish between package/module and
         its attribute part.
        """
        dot_idx = path.rfind('.')
        if dot_idx == -1:
            raise InvalidOperationPathError(path)
        module = self.import_module(path[:dot_idx])
        operation = getattr(module, path[dot_idx+1:])
        if not isinstance(operation, Callable):
            raise NotCallableError(path)
        return operation
