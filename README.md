# ubuild

Simple checkinstall based build script. To use in a project, simply include a .ubuild.json file in the project directory. That file should looks something like:

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

These are the currently supported options:

* `name` is the name of the project, and used in the debian package.
* `requires` is a list of system packages that the project depends on
* `build_requires` is a list of system packages required for building the project
* `pre_build_command` is a command to be run before building. It generally is used to set up the build environment, but not in any way that checkinstall should track (e.g. downloading non-system dependencies, building data files, etc.)
* `build_command` is the command that installs the files to the appropriate locations on the system. Checkinstall will run this command, and track filesystem changes, so do not put any setup or cleanup actions in this command.
* `post_build_command` is a command mostly for cleanup. It can also be used to push the debian file somewhere else if necessary.

To run the build system, first install ubuild. This can be done by pulling down the project and running:

    sudo python setup.py install

... or by installing a .deb of ubuild that has previously been built.

After it has been installed, simply run:

    sudo ubuild.py

...inside the project folder. Any failures will stop the build.

This currently expects a Debian-based system with apt-get available.
