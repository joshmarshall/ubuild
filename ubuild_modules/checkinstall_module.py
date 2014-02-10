import logging

from ubuild_modules import helpers


_LOGGER = logging.getLogger("checkinstall-module")


def prepare(context, config, execute):
    build_requires = config.get("build_requires", [])
    if "checkinstall" not in build_requires:
        build_requires.insert(0, "checkinstall")

    _LOGGER.debug(
        "Installing %d build requirements..." % (len(build_requires)))
    execute("apt-get update")
    execute("apt-get install -y %s" % (" ".join(build_requires)))

    _LOGGER.debug("Finished installing build requirements.")

    pre_command = config.get("command")
    if pre_command:
        _LOGGER.debug("Running pre command...")
        execute(pre_command)
        _LOGGER.debug("Finished running pre command.")


def build(context, config, execute):
    version = config.get("options.version") or \
        helpers.generate_datetime_version()
    build_command = config.get("command", "make install")
    replacements = {
        "name": config["project_name"],
        "requires": ",".join(config.get("project_requires", [])),
        "version": version,
        "command": build_command
    }

    checkinstall_command = \
        "checkinstall --showinstall=no -y --requires='%(requires)s' " \
        "--pkgname='%(name)s' --provides='%(name)s' --nodoc " \
        "--deldoc=yes --deldesc=yes --delspec=yes " \
        "--pkgversion='%(version)s' %(command)s" % (replacements)

    execute(checkinstall_command)
    _LOGGER.debug("Finished running checkinstall.")


def cleanup(context, config, execute):
    command = config["command"]
    _LOGGER.debug("Running cleanup...")
    execute(command)
    _LOGGER.debug("Finished running cleanup.")


def register(registry):
    registry.register("checkinstall.prepare", prepare)
    registry.register("checkinstall.build", build)
    registry.register("checkinstall.cleanup", cleanup)
