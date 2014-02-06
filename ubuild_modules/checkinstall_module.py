from ubuild_modules import helpers


class CheckinstallModule(object):

    def __init__(self, config):
        self._name = config["name"]
        self._version = config.get("options.version") or \
            helpers.generate_datetime_version()
        self._requires = config.get("project_requires", [])
        self._build_requires = config.get("build_requires", [])
        self._pre_command = config.get("pre_build_command")
        self._build_command = config["build_command"]
        self._post_command = config.get("post_build_command")

    def prep(self, execute):
        self._setup_system_requirements(execute)
        if self._pre_command:
            print "Running pre command..."
            execute(self._pre_command)
            print "Finished running pre command."
            print "------------------------------"

    def build(self, execute):
        replacements = {
            "name": self._name,
            "requires": ",".join(self._requires),
            "version": self._version,
            "command": self._build_command
        }

        checkinstall_command = \
            "checkinstall --showinstall=no -y --requires='%(requires)s' " \
            "--pkgname='%(name)s' --provides='%(name)s' --nodoc " \
            "--deldoc=yes --deldesc=yes --delspec=yes " \
            "--pkgversion='%(version)s' %(command)s" % (replacements)

        execute(checkinstall_command)
        print "Finished running checkinstall."
        print "------------------------------"

    def cleanup(self, execute):
        if self._post_command:
            print "Running post command..."
            execute(self._post_command)
            print "Finished running post command."
            print "------------------------------"

    def _setup_system_requirements(self, execute):
        if "checkinstall" not in self._build_requires:
            self._build_requires.insert(0, "checkinstall")

        print "Installing %d build requirements..." % (
            len(self._build_requires))
        execute("apt-get update")
        execute("apt-get install -y %s" % (" ".join(self._build_requires)))
        print "Finished installing build requirements."
        print "---------------------------------------"
