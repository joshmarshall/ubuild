import json
import os
# this is shlex.quote in 3.3
from pipes import quote
import sys
import tempfile

from ubuild_modules import checkinstall_module as checkinstall


def prepare_virtualenv(context, config, execute):
    config.setdefault("build_requires", [])
    config["build_requires"] += ["python-dev", "python-setuptools"]
    result = checkinstall.prepare(context, config, execute)
    execute("easy_install pip")
    execute("pip install virtualenv")
    return result


def build_virtualenv(context, config, execute):
    single_step_config = {
        "steps": [{
            "name": "virtualenv.execute",
            "virtualenv_path": config["virtualenv_path"],
            "requirements_files": config.get("requirements_files", []),
            "requirements_params": config.get("requirements_params", []),
            "download_path": config.get("download_path", None)
        }]
    }

    if config.get("download_path"):
        # we will download the packages first, and then use --find-links to
        # reduce additional downloading for this box.
        download_path = config["download_path"]
        execute("mkdir -p {}", download_path)
        requirements = config.get("requirements_files", [])
        command = ["pip install --download {}"]
        command += ["-r {}" for r in requirements]
        command += [" ".join(config.get("requirements_params"))]
        command = " ".join(command)
        execute(command, download_path, *requirements)

    with tempfile.NamedTemporaryFile() as temp_config:
        temp_config.write(json.dumps(single_step_config))
        temp_config.flush()

        command = "{} --config {}".format(
            quote(sys.argv[0]), quote(temp_config.name))
        config.setdefault("command", command)

        return checkinstall.build(context, config, execute)


def register(registry):
    registry.register("virtualenv.prepare", prepare_virtualenv)
    registry.register("virtualenv.build", build_virtualenv)
    registry.register("virtualenv.execute", execute_virtualenv)


def execute_virtualenv(context, config, execute):
    # this is a default replacement for build_command, sets up venv
    # and installs dependencies in a somewhat standard way.

    virtualenv_path = config["virtualenv_path"]
    virtualenv_base = os.path.dirname(config["virtualenv_path"])
    virtualenv_requirements = config.get("requirements_files", [])
    virtualenv_params = config.get("requirements_params", [])
    download_path = config.get("download_path")

    execute("mkdir -p {}", virtualenv_base)
    execute("virtualenv {} --always-copy", virtualenv_path)

    if virtualenv_requirements:
        commands = ["{}/bin/pip install -I".format(virtualenv_path)]
        arguments = []

        if download_path:
            commands.append("--no-index --find-links file://{}")
            arguments.append(download_path)

        commands += ["-r {}" for r in virtualenv_requirements]
        arguments += virtualenv_requirements

        if virtualenv_params:
            commands.append(" ".join(virtualenv_params))

        command = " ".join(commands)
        execute(command, *arguments)

    execute("{}/bin/python setup.py install".format(virtualenv_path))
