import datetime
import ubuild
from tests import helpers


class TestuBuild(helpers.RunnerTestCase):

    @helpers.use_config(helpers.SIMPLE_CONFIG)
    @helpers.set_options(version="1234")
    def test_main(self):
        ubuild.main()
        self.assert_opened_config_file(".ubuild.json")
        self.assert_calls([
            "apt-get update",
            "apt-get install -y checkinstall package",
            "checkinstall --showinstall=no -y --requires='package' "
            "--pkgname='foobar' --provides='foobar' --nodoc --deldoc=yes "
            "--deldesc=yes --delspec=yes --pkgversion='1234' "
            "make install"
        ])

    @helpers.use_config(helpers.SIMPLE_CONFIG)
    def test_default_version(self):
        ubuild.main()
        for name, args, kwargs in self.calls:
            if args[0].startswith("checkinstall"):
                now = datetime.datetime.utcnow().strftime("%Y%m%d.%H%M%S")
                expected_version = "--pkgversion='%s'" % (now)
                self.assertTrue(
                    expected_version in args[0],
                    "the version should default to a datetime string.")
                return

        self.fail("No checkinstall command was run.")

    @helpers.use_config(helpers.SIMPLE_CONFIG)
    @helpers.set_options(config_file="foo.json")
    def test_specified_config_file(self):
        ubuild.main()
        self.assert_opened_config_file("foo.json")

    @helpers.use_config(helpers.VIRTUALENV_CONFIG)
    @helpers.set_options(version="1234", config_file="foo.json")
    def test_virtualenv_module(self):
        ubuild.main()
        self.assert_calls([
            "apt-get update",
            "apt-get install -y checkinstall libcurl python-dev "
            "python-setuptools",
            "easy_install pip",
            "pip install virtualenv",
            "checkinstall --showinstall=no -y --requires='libcurl' "
            "--pkgname='foojson' --provides='foojson' --nodoc "
            "--deldoc=yes --deldesc=yes --delspec=yes "
            "--pkgversion='1234' ubuild.py --build_module --config=foo.json"
        ])

    @helpers.use_config(helpers.VIRTUALENV_CONFIG)
    @helpers.set_options(build_module=True)
    def test_virtualenv_build(self):
        ubuild.main()
        self.assert_calls([
            "mkdir -p /opt/venv",
            "virtualenv /opt/venv/virtual --always-copy",
            #"source /opt/venv/virtual/activate",
            "/opt/venv/virtual/bin/pip install -r requirements.txt "
            "--allow-all-external",
            "/opt/venv/virtual/bin/pip install -r extra-reqs.txt "
            "--allow-all-external",
            "/opt/venv/virtual/bin/python setup.py install"
        ])
