# ubuild

This is a simple build project that aims to help standardize project package building. The "built-in" focus is around making single .deb files for a project, and it uses checkinstall to do this. (There is a virtualenv wrapper that helps specifically for Python projects.) However, the system itself is simple enough that most build processes should be able to leverage it.

The idea is pretty simple: every project has a `.ubuild.json` file in the root. After installing this project (probably in a clean build environment), you simply run `ubuild` (maybe with some parameters) and at the other end you can do what you would like with the artifact(s).

The following is a simple `.ubuild.json` example, using the built-in checkinstall module.

    {
      "name": "ubuild",
      "build_module": "checkinstall",
      "build_requires": ["lib-thingy","lib-build-dependency"]
      "project_requires": ["lib-thingy"],
      "build_command": "make install"
    }

This would result in a .deb file that you could push to a repo, secure storage, whatever, and use in deployment or additional build steps. (For instance, creating a Packer image, in the next example.)


## Build Modules

ubuild works by calling simple Python modules that can be provided by the user. (The CheckinstallModule and VirtualEnvModule are automatically available, and more will be added over time.) Let's say after you've updated one or more of your individual projects and created .deb files for each one, you want to build a Packer image (http://packer.io). You could write a module like:


    from ubuild_modules import registry

    class PackerModule(object):

        def __init__(self, config):
            self._aws_key = os.env["MY_AMAZON_KEY"]
            self._aws_secret = os.env["MY_AMAZON_SECRET"]
            self._packer_config_file = config["packer_file"]

        def prep(self, execute):
            # maybe you need to download environment variables,
            # prep packer, etc. Could also be a no-op, like this
            # example. Execute can be used for shell calls,
            # just pass it a string.
            pass

        def build(self, execute):
            execute(
                "packer -var 'aws_access_key=%s' "
                "-var 'aws_secret_key=%s' %s" % (
                    self._aws_key, self._aws_secret,
                    self._packer_config_file))

        def cleanup(self, execute):
            # ping a deploy service, delete extra files, whatever.
            pass

    registry.register_module("packer", PackerModule)

At the end of this process there would be a new image in Amazon. If you wanted to parse the output of the system call programmatically, you can just use `subprocess.Popen` yourself and ignore the `execute` argument. A config file that used this might look like:

    {
      "module_import": "mymodules.packer_module",
      "build_module": "packer",
      "packer_file": "packer.json"
    }

We provide a `module_import` argument, which just needs to be an import to a Python file that calls `ubuild_modules.registry.register_module`. In this example, we put the actual code in the same file, but you could build out your own repository of ubuild modules that you install on your build machines, and have a single module that you import that registers all of them at once.

So, in summary, do the following things:

* Implement a class that has `prep`, `build`, and `cleanup` methods.
* Call `ubuild_modules.registry.register_module` somewhere.
* Provide a `module_import` in the `.ubuild.json` file that points where the module(s) are registered.


## Checkinstall

The checkinstall (and virtualenv) module currently expect a Debian-based system with apt-get available. These are the currently supported options for the checkinstall-based modules:

* `name` is the name of the project, and used in the debian package.
* `requires` is a list of system packages that the project depends on
* `build_requires` is a list of system packages required for building the project
* `pre_build_command` is a command to be run before building. It generally is used to set up the build environment, but not in any way that checkinstall should track (e.g. downloading non-system dependencies, building data files, etc.)
* `build_command` is the command that installs the files to the appropriate locations on the system. Checkinstall will run this command, and track filesystem changes, so do not put any setup or cleanup actions in this command.
* `post_build_command` is a command mostly for cleanup. It can also be used to push the debian file somewhere else if necessary, or even kick off deployment or other build jobs.
* `build_module` is required for all configuration files, and should be `checkinstall` for building deb files.

To run the build system, first install ubuild. This can be done by pulling down the project and running:

    sudo python setup.py install

... or by installing a .deb of ubuild that has previously been built.

After it has been installed, simply run:

    sudo ubuild

...inside the project folder. Any failures will stop the build.

The current command line options are:

* `--version` which allows you to provide at build time a version to be used. Be aware that using non-incrementing version numbers may break workflows that depend on autoupdating...
* `--config` which allows you to point to an alternate JSON file than the .ubuild.json default
* `--build_module` which you will probably never use. This will be leveraged by modules who want to provide a default `build_as_standalone` operation, replacing the `make install` step, `python setup.py install`, etc.


## Virtualenvs

Using the virtualenv module might look like:

    {
      "name": "ubuild",
      "build_module": "virtualenv",
      "virtualenv_path": "/opt/ubuild/venv",
      "requirements_paths": ["requirements.txt"],
      "requirements_args": ["--allow-all-external"]
    }

We first set `build_module` to `virtualenv`. The other required argument is `virtualenv_path`, which tells ubuild where to create the new virtualenv. `requirements_paths` is a list of PyPI dependency files, which is usually one or more `requirements.txt` in Python projects. `requirements_args` are just additional parameters to pass to the `pip install -r %s` command, in this case allowing external packages through PyPI. If no outer `build_command` is provided, this module will run `$VENV_PATH/bin/python setup.py install`.


As always, I welcome feedback, horror stories, or general internet anger.
