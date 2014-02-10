import optparse
import os
from ubuild_modules import checkinstall_module as checkinstall
from ubuild_modules import helpers


def prepare_virtualenv(context, config, execute):
    config.setdefault("build_requires", [])
    config["build_requires"] += ["python-dev", "python-setuptools"]
    result = checkinstall.prepare(context, config, execute)
    execute("easy_install pip")
    execute("pip install virtualenv")
    return result


def build_virtualenv(context, config, execute):
    allow_external = config.get("allow_external_requirements", True)
    requirements_paths = ",".join(config.get("requirements_files", []))

    options = {
        "path": config["virtualenv_path"]
    }

    if requirements_paths:
        options["requirements"] = requirements_paths
    if allow_external:
        options["allow-external"] = ""

    options = ["--%s %s" % (name, value) for name, value in options.items()]

    config.setdefault(
        "command",
        "python -m ubuild_modules.virtualenv_module %s" % " ".join(options))
    return checkinstall.build(context, config, execute)


def register(registry):
    registry.register("virtualenv.prepare", prepare_virtualenv)
    registry.register("virtualenv.build", build_virtualenv)


def main():
    # this is a default replacement for build_command, sets up venv
    # and installs dependencies in a somewhat standard way.
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("-p", "--path", help="virtualenv path", dest="path")
    opt_parser.add_option(
        "-e", "--allow-external", help="allow external requirements",
        action="store_true")
    opt_parser.add_option(
        "-r", "--requirements", dest="requirements", default=None,
        help="comma-separated list of requirements files")

    options, _ = opt_parser.parse_args()
    virtualenv_base = os.path.dirname(options.path)

    helpers.execute("mkdir -p %s" % (virtualenv_base))
    helpers.execute("virtualenv %s --always-copy" % (options.path))
    #execute("source %s/activate" % (self._path))
    if options.requirements:
        requirements = " ".join(
            ["-r %s" % (r) for r in options.requirements.split(",")])
        command = "%s/bin/pip install -I %s" % (
            options.path, requirements)
        if options.allow_external:
            command += " --allow-all-external"
        helpers.execute(command)
    helpers.execute(
        "%s/bin/python setup.py install" % (options.path))


if __name__ == "__main__":
    main()
