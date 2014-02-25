import datetime
import mock
import ubuild_modules.runner
import ubuild_modules.checkinstall_module
from tests import helpers


SUCCESSFUL_OUTPUT = """

2 -  Name:    [ ubuild ]
3 -  Version: [ 20140222.101742 ]
4 -  Release: [ 1 ]
5 -  License: [ GPL ]
6 -  Group:   [ checkinstall ]
7 -  Architecture: [ amd64 ]

**********************************************************************

 Done. The new package has been installed and saved to

 /vagrant/ubuild_20140222.101742-1_amd64.deb

 You can remove it from your system anytime using:

      dpkg -r ubuild

**********************************************************************
"""


class TestuBuild(helpers.RunnerTestCase):

    @helpers.use_config(helpers.SIMPLE_CONFIG)
    @helpers.set_options(version="1234")
    def test_main(self):
        ubuild_modules.runner.main()
        self.mock_config.assert_opened_config_file(".ubuild.json")
        self.assert_calls([
            "apt-get update",
            "apt-get install -y checkinstall package",
            "checkinstall -y --requires=package "
            "--pkgname=foobar --provides=foobar --nodoc --deldoc=yes "
            "--deldesc=yes --delspec=yes --backup=no --pkgversion=1234 "
            "make install"
        ])

    @helpers.use_config(helpers.SIMPLE_CONFIG)
    def test_default_version(self):
        ubuild_modules.runner.main()
        for name, args, kwargs in self.calls:
            if args[0].startswith("checkinstall"):
                now = datetime.datetime.utcnow().strftime("%Y%m%d.%H%M%S")
                expected_version = "--pkgversion={}".format(now)
                self.assertTrue(
                    expected_version in args[0],
                    "the version should default to a datetime string.")
                return

        self.fail("No checkinstall command was run.")

    @helpers.use_config(helpers.SIMPLE_CONFIG)
    @helpers.set_options(config_file="foo.json")
    def test_specified_config_file(self):
        ubuild_modules.runner.main()
        self.mock_config.assert_opened_config_file("foo.json")

    @mock.patch("ubuild_modules.helpers.generate_datetime_version")
    def test_build_context_has_deb_path(self, mock_version):
        mock_version.return_value = "20140222.101742"
        context = {}
        config = {
            "project_name": "ubuild"
        }

        self.execute_output = SUCCESSFUL_OUTPUT

        ubuild_modules.checkinstall_module.build(
            context, config, self.execute)
        self.assertTrue("checkinstall_deb_path" in context)
        self.assertEqual(
            "/vagrant/ubuild_20140222.101742-1_amd64.deb",
            context["checkinstall_deb_path"])

    @mock.patch("os.remove")
    @mock.patch("os.path.exists")
    def test_cleanup_removes_deb(self, mock_exists, mock_remove):
        mock_exists.return_value = True

        context = {
            "checkinstall_deb_path": "/what/foobar.deb"
        }

        config = {
            "name": "checkinstall.cleanup",
            "commands": ["mv $C:CHECKINSTALL_DEB_PATH foo.deb"]
        }

        ubuild_modules.checkinstall_module.cleanup(
            context, config, self.execute)
        mock_exists.assert_called_with("/what/foobar.deb")
        mock_remove.assert_called_with("/what/foobar.deb")

        self.assertEqual(["mv /what/foobar.deb foo.deb"], self.commands)
