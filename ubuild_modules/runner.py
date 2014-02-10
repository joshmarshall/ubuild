#!/usr/bin/env python

import importlib
import json
import optparse
import os

from ubuild_modules import helpers
from ubuild_modules.registry import Registry


_DEFAULT_JSON_FILE = ".ubuild.json"
_DEFAULT_IMPORT_MODULES = [
    "ubuild_modules.virtualenv_module",
    "ubuild_modules.checkinstall_module"
]


def load_configuration(config_file):
    if not os.path.exists(config_file):
        raise RuntimeError("Cannot find %s file." % (config_file))
    with open(config_file) as build_file:
        build_contents = build_file.read()
    build_config = json.loads(build_contents)

    return build_config


def main():
    option_parser = optparse.OptionParser()
    option_parser.add_option(
        "-v", "--version", dest="version", default=None,
        help="set the version of the output package")
    option_parser.add_option(
        "-c", "--config", dest="config_file", default=None,
        help="use a specific config file instead of .ubuild.json")
    option_parser.add_option(
        "-m", "--build_module", dest="build_module", default=False,
        action="store_true",
        help="run build command for the module, if applicable")

    options, _ = option_parser.parse_args()
    config_file = options.config_file or _DEFAULT_JSON_FILE
    config = load_configuration(config_file)

    options = {
        "options.config": options.config_file,
        "options.version": options.version
    }

    registry = Registry()

    import_modules = config.get("import_modules", [])
    import_modules = set(import_modules + _DEFAULT_IMPORT_MODULES)
    for module_name in import_modules:
        module = importlib.import_module(module_name)
        module.register(registry)

    context = {}
    for step_configuration in config["steps"]:
        step_name = step_configuration.pop("name")
        step_configuration.update(options)
        context = registry.execute(
            step_name, context, step_configuration, helpers.execute)
