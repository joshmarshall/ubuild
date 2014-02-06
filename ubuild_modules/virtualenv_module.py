import os
from ubuild_modules import checkinstall_module


class VirtualEnvModule(checkinstall_module.CheckinstallModule):

    def __init__(self, config):
        config.setdefault("build_requires", [])
        config["build_requires"] += ["python-dev", "python-setuptools"]

        # this is a bit hacky...
        options = []
        for config_name, config_value in config.items():
            if config_name.startswith("options.") and config_value:
                options.append(
                    "--%s=%s" % (config_name[8:], config_value))

        config.setdefault(
            "build_command",
            "ubuild --build_module %s" % " ".join(options))

        # intercepting requirements for checkinstall... this hints at the
        # need for a signal / event system instead of tight coupling and
        # construction order dependency...

        super(VirtualEnvModule, self).__init__(config)

        self._virtualenv_path = config["virtualenv_path"]
        self._virtualenv_base = os.path.dirname(self._virtualenv_path)
        self._requirement_paths = config.get("requirements_files", [])
        self._requirement_args = " ".join(
            config.get("requirements_params", []))

    def prep(self, execute):
        # do the normal checkinstall preparation...
        super(VirtualEnvModule, self).prep(execute)

        # ...and now set up python / virtualenv environment.
        execute("easy_install pip")
        execute("pip install virtualenv")

    # We don't implement a `build` because checkinstall works fine as
    # long as we override the build command (as above).

    def build_as_standalone(self, execute):
        # this is a default replacement for build_command, sets up venv
        # and installs dependencies in a somewhat standard way.

        execute("mkdir -p %s" % (self._virtualenv_base))
        execute("virtualenv %s --always-copy" % (self._virtualenv_path))
        #execute("source %s/activate" % (self._virtualenv_path))
        for requirement_path in self._requirement_paths:
            execute("%s/bin/pip install -r %s %s" % (
                self._virtualenv_path, requirement_path,
                self._requirement_args))
        execute("%s/bin/python setup.py install" % (self._virtualenv_path))
