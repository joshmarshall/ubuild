# ubuild

This is a simple checkinstall based build script. To use in a project, simply include a .ubuild.json file in the project directory. That file should looks something like:

    {
        "name": "ubuild",
        "build_requires": [
            "python-setuptools"
        ]
        "requires": [
            "python-setuptools"
        ],
        "build_command": "python setup.py install"
    }

This currently expects a Debian-based system with apt-get available.

These are the currently supported options for the configuration file:

* `name` is the name of the project, and used in the debian package.
* `requires` is a list of system packages that the project depends on
* `build_requires` is a list of system packages required for building the project
* `pre_build_command` is a command to be run before building. It generally is used to set up the build environment, but not in any way that checkinstall should track (e.g. downloading non-system dependencies, building data files, etc.)
* `build_command` is the command that installs the files to the appropriate locations on the system. Checkinstall will run this command, and track filesystem changes, so do not put any setup or cleanup actions in this command.
* `post_build_command` is a command mostly for cleanup. It can also be used to push the debian file somewhere else if necessary.
* `build_module` is an idea for allowing standard packing processes. Right now it just supports virtualenv (below)

To run the build system, first install ubuild. This can be done by pulling down the project and running:

    sudo python setup.py install

... or by installing a .deb of ubuild that has previously been built.

After it has been installed, simply run:

    sudo ubuild.py

...inside the project folder. Any failures will stop the build.

The current command line options are:

* `--version` which allows you to provide at build time a version to be used. Be aware that using non-incrementing version numbers may break workflows that depend on autoupdating...
* `--config` which allows you to point to an alternate JSON file than the .ubuild.json default
* `--build_module` which you will probably never use. This will be leveraged by modules who want to provide a default `build_command` operation, replacing the `make install` step, `python setup.py install`, etc.

## Virtualenvs / Modules

Right now, there is an optional virtualenv module that can be used to create, prep, and package a virtualenv into a .deb for deployment. An example file might look like:

```
{
  "name": "ubuild",
  "build_requires": ["python-setuptools"],
  "requires": ["python-setuptools"],
  "build_module": {
    "name": "virtualenv",
    "virtualenv_path": "/opt/ubuild/venv",
    "requirements": ["requirements.txt"],
    "requirements_args": ["--allow-all-external"]
  }
}
```

The key item here is `build_module`, which has a set of configuration options specific to the module. In this case, `virtualenv_path` (which is required) tells ubuild where to create the new virtualenv. `requirements` is a list of PyPI dependencies, which is usually `requirements.txt` in Python projects. `requirements_args` are just additional parameters to pass to the `pip install -r %s` command, in this case allowing external packages through PyPI.

As always, I welcome feedback, horror stories, or general internet poor behavior.

