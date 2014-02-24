import logging
import os

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

    for command in config.get("commands", []):
        command = helpers.update_command(context, command)
        execute(command)


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
        "--deldoc=yes --deldesc=yes --delspec=yes --backup=no " \
        "--pkgversion='%(version)s' %(command)s" % (replacements)

    stdout = execute(checkinstall_command)
    path = None
    check_row = False
    for row in stdout.splitlines():
        if "Done. The new package has been installed and saved to" in row:
            check_row = True
            continue

        if not check_row:
            continue

        if "%s_%s" % (config["project_name"], version) in row:
            path = row.strip()
            context["checkinstall_deb_path"] = path
            break

    _LOGGER.debug("Finished running checkinstall.")


def cleanup(context, config, execute):
    _LOGGER.debug("Running cleanup...")

    for command in config.get("commands", []):
        command = helpers.update_command(context, command)
        execute(command)

    if os.path.exists(context["checkinstall_deb_path"]):
        os.remove(context["checkinstall_deb_path"])

    _LOGGER.debug("Finished running cleanup.")


def register(registry):
    registry.register("checkinstall.prepare", prepare)
    registry.register("checkinstall.build", build)
    registry.register("checkinstall.cleanup", cleanup)
