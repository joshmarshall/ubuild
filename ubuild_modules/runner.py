#!/usr/bin/env python

import importlib
import json
import optparse
import os
import subprocess

from ubuild_modules import registry


_DEFAULT_JSON_FILE = ".ubuild.json"
_DEFAULT_BUILD_MODULE = "checkinstall"


def load_configuration(config_file):
    if not os.path.exists(config_file):
        raise RuntimeError("Cannot find %s file." % (config_file))
    with open(config_file) as build_file:
        build_contents = build_file.read()
    build_config = json.loads(build_contents)

    return build_config


def call(command):
    result = subprocess.call(command, shell=True)
    if result != 0:
        raise RuntimeError("Could not execute command (%d): %s" % (
            result, command))


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

    config["options.config"] = options.config_file
    config["options.version"] = options.version

    extra_module_name = config.get("module_import")
    if extra_module_name:
        importlib.import_module(extra_module_name)

    module = registry.create_module(config["build_module"], config)

    if options.build_module:
        return module.build_as_standalone(call)

    module.prep(call)
    module.build(call)
    module.cleanup(call)
