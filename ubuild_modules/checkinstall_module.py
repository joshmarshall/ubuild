import os

from ubuild_modules import helpers
from ubuild_modules.logger import LOGGER


def prepare(context, config, execute):
    build_requires = config.get("build_requires", [])
    if "checkinstall" not in build_requires:
        build_requires.insert(0, "checkinstall")

    LOGGER.debug(
        "Installing {} build requirements...".format(len(build_requires)))
    if build_requires:
        execute("apt-get update")
        command = "apt-get install -y " + " ".join(map(
            lambda x: "{}", build_requires))
        execute(command, *build_requires)

    LOGGER.debug("Finished installing build requirements.")

    for command in config.get("commands", []):
        command = helpers.update_command(context, command)
        execute(command)


def build(context, config, execute):
    version = config.get("options.version") or \
        helpers.generate_datetime_version()
    build_command = config.get("command", "make install")
    replacements = {
        "build_name": config["project_name"],
        "build_requires": ",".join(config.get("project_requires", [])),
        "build_version": version,
        "build_command": build_command
    }

    checkinstall_command = \
        "checkinstall --showinstall=no -y --requires={build_requires} " \
        "--pkgname={build_name} --provides={build_name} --nodoc " \
        "--deldoc=yes --deldesc=yes --delspec=yes --backup=no " \
        "--pkgversion={build_version} {build_command}"

    stdout = execute(checkinstall_command, **replacements)
    path = None
    check_row = False
    for row in stdout.splitlines():
        if "Done. The new package has been installed and saved to" in row:
            check_row = True
            continue

        if not check_row:
            continue

        if "{}_{}".format(config["project_name"], version) in row:
            path = row.strip()
            context["checkinstall_deb_path"] = path
            break

    LOGGER.debug("Finished running checkinstall.")


def cleanup(context, config, execute):
    LOGGER.debug("Running cleanup...")

    for command in config.get("commands", []):
        command = helpers.update_command(context, command)
        execute(command)

    if os.path.exists(context["checkinstall_deb_path"]):
        os.remove(context["checkinstall_deb_path"])

    LOGGER.debug("Finished running cleanup.")


def register(registry):
    registry.register("checkinstall.prepare", prepare)
    registry.register("checkinstall.build", build)
    registry.register("checkinstall.cleanup", cleanup)
