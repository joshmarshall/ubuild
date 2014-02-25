class Registry(object):

    def __init__(self):
        self._registry = {}

    def register(self, module_name, module):
        self._registry[module_name] = module

    def execute(self, module_name, *args, **kwargs):
        if module_name not in self._registry:
            raise InvalidModule(
                "Module '{}' is not registered".format(module_name))
        return self._registry[module_name](*args, **kwargs)


class InvalidModule(Exception):
    """Raised when registering or executing an invalid module."""
    pass
