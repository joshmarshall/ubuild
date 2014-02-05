#!/usr/bin/env python

from datetime import datetime
import json
import optparse
import os
import subprocess


DEFAULT_JSON_FILE = ".ubuild.json"


def load_configuration(config_file):
    if not os.path.exists(config_file):
        raise RuntimeError("Cannot find %s file." % (config_file))
    with open(config_file) as build_file:
        build_contents = build_file.read()
    build_config = json.loads(build_contents)
    build_config["config_file"] = config_file
    return build_config


def setup_system_requirements(config):
    build_requires = config.get("build_requires", [])
    if "checkinstall" not in build_requires:
        build_requires.insert(0, "checkinstall")

    print "Installing %d build requirements..." % (len(build_requires))
    call("apt-get update")
    call("apt-get install -y %s" % (" ".join(build_requires)))
    print "Finished installing build requirements."
    print "---------------------------------------"


def call(command):
    result = subprocess.call(command, shell=True)
    if result != 0:
        raise RuntimeError("Could not execute command (%d): %s" % (
            result, command))


def get_version():
    return datetime.utcnow().strftime("%Y%m%d.%H%M%S")


def run_checkinstall(name, requires, version, command):
    replacements = {
        "name": name,
        "requires": ",".join(requires),
        "version": version,
        "command": command
    }

    checkinstall_command = \
        "checkinstall --showinstall=no -y --requires='%(requires)s' " \
        "--pkgname='%(name)s' --provides='%(name)s' --nodoc --deldoc=yes " \
        "--deldesc=yes --delspec=yes --pkgversion='%(version)s' " \
        "%(command)s" % replacements

    call(checkinstall_command)
    print "Finished running checkinstall."
    print "------------------------------"


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
    config_file = options.config_file or DEFAULT_JSON_FILE
    config = load_configuration(config_file)

    module_config = config.get("build_module")
    module = None

    if module_config:
        print "Updating config for module '%s'..." % (module_config["name"])
        module = _module_registry[module_config["name"]](module_config)
        module.update_config(config)

    if options.build_module:
        # this is a default replacement for build_command, sets up venv
        # and installs dependencies in a somewhat standard way.
        return module.run_build()

    setup_system_requirements(config)
    version = options.version or get_version()

    pre_command = config.get("pre_build_command")
    if pre_command:
        print "Running pre command..."
        call(pre_command)
        print "Finished running pre command."
        print "------------------------------"

    if module:
        module.prep_build()

    command = config["build_command"]
    run_checkinstall(
        name=config["name"], requires=config.get("requires", []),
        version=version, command=command)

    post_command = config.get("post_build_command")
    if post_command:
        print "Running post command..."
        call(post_command)
        print "Finished running post command."
        print "------------------------------"


class _VirtualEnvModule(object):

    def __init__(self, module_config):
        self._module_config = module_config
        self._virtualenv_path = module_config["virtualenv_path"]
        self._virtualenv_base = os.path.dirname(self._virtualenv_path)
        self._requirement_paths = module_config.get("requirements", [])
        self._requirement_args = " ".join(
            module_config.get("requirements_params", []))

    def update_config(self, config):
        config["build_requires"] += ["python-dev", "python-setuptools"]
        config.setdefault(
            "build_command", "ubuild.py --build_module --config=%s" % (
                config["config_file"]))

    def prep_build(self):
        # feels like this could be added another way... make pre_command
        # a list instead?
        call("easy_install pip")
        call("pip install virtualenv")

    def run_build(self):
        call("mkdir -p %s" % (self._virtualenv_base))
        call("virtualenv %s --always-copy" % (self._virtualenv_path))
        #call("source %s/activate" % (self._virtualenv_path))
        for requirement_path in self._requirement_paths:
            call("%s/bin/pip install -r %s %s" % (
                self._virtualenv_path, requirement_path,
                self._requirement_args))
        call("%s/bin/python setup.py install" % (self._virtualenv_path))


_module_registry = {
    "virtualenv": _VirtualEnvModule
}


if __name__ == "__main__":
    main()
