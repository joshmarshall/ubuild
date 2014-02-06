# built-ins...
from ubuild_modules import checkinstall_module
from ubuild_modules import virtualenv_module


_MODULE_REGISTRY = {}


def register_module(module_name, module):
    _MODULE_REGISTRY[module_name] = module


def create_module(module_name, module_configuration):
    return _MODULE_REGISTRY[module_name](module_configuration)


register_module("checkinstall", checkinstall_module.CheckinstallModule)
register_module("virtualenv", virtualenv_module.VirtualEnvModule)
