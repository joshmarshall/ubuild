import json
import os
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
            "requirements_params": config.get("requirements_params", [])
        }]
    }

    with tempfile.NamedTemporaryFile() as temp_config:
        temp_config.write(json.dumps(single_step_config))
        temp_config.flush()

        command = "%s --config '%s'" % (sys.argv[0], temp_config.name)
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

    execute("mkdir -p %s" % (virtualenv_base))
    execute("virtualenv %s --always-copy" % (virtualenv_path))

    if virtualenv_requirements:
        requirements = " ".join(
            ["-r %s" % (r) for r in virtualenv_requirements])
        command = "%s/bin/pip install -I %s" % (virtualenv_path, requirements)
        if virtualenv_params:
            command += " " + " ".join(virtualenv_params)
        execute(command)
    execute("%s/bin/python setup.py install" % (virtualenv_path))
