#!/usr/bin/env python

from datetime import datetime
import json
import optparse
import os
import subprocess


DEFAULT_JSON_FILE = ".ubuild.json"


def load_configuration(config_file):
    config_file = config_file or DEFAULT_JSON_FILE
    if not os.path.exists(config_file):
        raise RuntimeError("Cannot find %s file." % (config_file))
    with open(config_file) as build_file:
        build_contents = build_file.read()
    build_config = json.loads(build_contents)
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
    options, _ = option_parser.parse_args()

    config = load_configuration(options.config_file)
    setup_system_requirements(config)
    version = options.version or get_version()

    pre_command = config.get("pre_build_command")
    if pre_command:
        print "Running pre command..."
        call(pre_command)
        print "Finished running pre command."
        print "------------------------------"

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


if __name__ == "__main__":
    main()
