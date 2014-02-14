[![Build Status](https://travis-ci.org/joshmarshall/ubuild.png?branch=master)](https://travis-ci.org/joshmarshall/ubuild)
# ubuild

STATUS: Toy project.

This is a simple project that helps me build small projects / dependencies. The "built-in" focus is around making single .deb files for a project, and it uses checkinstall to do this. (There is a virtualenv wrapper that helps specifically for Python projects.)

The idea is pretty simple: every project has a `.ubuild.json` file in the root. After installing this project (probably in a clean build environment), you simply run `ubuild` (maybe with some parameters) and at the other end you can do what you would like with the artifact(s). I usually shove the .deb up on a private HTTP server, and then deployment is as simple as "wget thing.db && dpkg -i thing.deb && apt-get install -f". (Environment variables / config would have been setup at server creation...)

To run the build system, first install ubuild. This can be done by pulling down the project and running:

    sudo python setup.py install

... or by installing a .deb of ubuild that has previously been built. :)

After it has been installed, simply run:

    sudo ubuild

...inside the project folder. Any failures will stop the build.

The following is a simple `.ubuild.json` example, using the built-in checkinstall module.

    {
      "steps": [{
        "name": "checkinstall.prepare",
        "build_requires": ["lib-thingy","lib-build-dependency"]
        "command": "make"
      }, {
        "name": "checkinstall.build",
        "project_name": "my-project",
        "project_requires": ["lib-thingy"],
        "command": "make install"
      }, {
        "name": "checkinstall.cleanup",
        "command": "make clean"
      }]
    }

This would result in a .deb file that you could push to a repo, secure storage, whatever, and use in deployment or additional build steps. (For instance, creating a Packer image, in the next example.)

The current command line options are:

* `--version` which allows you to provide at build time a version to be used. Be aware that using non-incrementing version numbers may break workflows that depend on autoupdating...
* `--config` which allows you to point to an alternate JSON file than the .ubuild.json default

## Build Modules

ubuild works by calling simple Python modules that can be provided by the user. (checkinstall and virtualenv are automatically available, and more will be added over time.) Let's say after you've updated one or more of your individual projects and created .deb files for each one, you want to build a Packer image (http://packer.io). You could write a module like:

    import os

    def build(context, config, execute):
        # context is a shared dictionary across steps.
        # config is the provided module configuration
        # execute is a simple wrapper around subprocess.Popen
        aws_key = os.env["MY_AMAZON_KEY"]
        aws_secret = os.env["MY_AMAZON_SECRET"]
        packer_config_file = config["packer_file"]
        execute(
            "packer -var 'aws_access_key=%s' "
            "-var 'aws_secret_key=%s' %s" % (
                self._aws_key, self._aws_secret,
                self._packer_config_file))
        # provide any information to pass on to other modules
        context["packer.image"] = "my-new-image-id"

    # all ubuild modules must have a 'register' function that
    # takes a registry object.
    def register(registry):
        registry.register("packer.build", build)

At the end of this process there would be a new image in Amazon. If you wanted to parse the output of the system call programmatically, you can just use `subprocess.Popen` yourself and ignore the `execute` argument. A config file that used this might look like:

    {
      "import_modules": ["mymodules.packer_module"],
      "steps": [{
        "name": "checkinstall.build",
        ... build a deb, push it to a repo, etc ...
      }, {
        "name": "packer.build",
        "packer_file": "packer.json"
      }]
    }

We provide a `import_modules` argument, which is a list of one or importable modules that define a `register` function. In this example, we put the actual code in the same file, but you could build out your own repository of ubuild modules that you install on your build machines, and have a single module that you import that registers all of them at once for simplicity.

So, in summary, do the following things:

* Implement functions that take a `context`, `config`, and `execute`.
* Implement a `register` function that accepts a `registry` argument, and call `registry.register` with the module name and callable to register your module(s).
* Provide a `import_modules` list in the `.ubuild.json` file that points where the module(s) are registered.


## Checkinstall

The checkinstall (and virtualenv) module currently expect a Debian-based system with apt-get available. These are the currently supported options for the checkinstall-based modules:

* Step `checkinstall.prepare`
    * Installs the necessary system libraries to run checkinstall. Takes the following arguments:
    * `build_requires`: a list of build dependencies to be install via apt-get
    * `command`: an optional command to be run after the build dependencies are install
* Step `checkinstall.build`
    * Runs checkinstall with the appropriate arguments and the provided command. Takes the following arguments:
    * `project_name`: the name of the project, used by the debian file
    * `project_requires`: any optional system dependencies that should be required when installing the deb
    * `command`: an optional command to be provided to checkinstall. If not specified, `make install` is the default.
* Step `checkinstall.cleanup`
    * Performs and follow-up actions.
    * `command`: a command to be run after the build is complete.
    * (not implemented yet: will automatically clean up build docs, etc.)


## Virtualenvs

Using the virtualenv module might look like:

    {
      "steps": [{
        "name": "virtualenv.prepare",
        "build_requires": ["libcurl4-openssl-dev"]
      }, {
        "name": "virtualenv.build",
        "project_name": "foobar",
        "virtualenv_path": "/opt/ubuild/venv",
        "requirements_files": ["requirements.txt"],
      }
    }

These steps are extra wrappers to `checkinstall` based operations.

* Step `virtualenv.prepare`
    * Wraps the checkinstall process, providing a few additional requirements. Takes the same options as `checkinstall.prepare`.
* Step `virtualenv.build`
    * Builds a virtualenv, installs the python dependencies, and installs the project, all through checkinstall.
    * Takes the following arguments, in addition to `checkinstall.build` commands:
    * `virtualenv_path`: the installed location of the virtualenv on the system
    * `requirements_files`: list of requirements files to install to the virtualenv
    * `command`: the optional command to pass to checkinstall. If none is provided, $VENV/bin/python setup.py install is used.
