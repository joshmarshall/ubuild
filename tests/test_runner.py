import datetime
import mock

import ubuild_modules.runner
from tests import helpers


class TestuBuild(helpers.RunnerTestCase):

    _ubuild_config = helpers.SIMPLE_CONFIG

    @helpers.set_options(version="1234")
    def test_main(self):
        ubuild_modules.runner.main()
        self.assert_opened_config_file(".ubuild.json")
        self.assert_calls([
            "apt-get update",
            "apt-get install -y checkinstall package",
            "checkinstall --showinstall=no -y --requires='package' "
            "--pkgname='foobar' --provides='foobar' --nodoc --deldoc=yes "
            "--deldesc=yes --delspec=yes --pkgversion='1234' "
            "make install"
        ])

    def test_default_version(self):
        ubuild_modules.runner.main()
        for name, args, kwargs in self.calls:
            if args[0].startswith("checkinstall"):
                now = datetime.datetime.utcnow().strftime("%Y%m%d.%H%M%S")
                expected_version = "--pkgversion='%s'" % (now)
                self.assertTrue(
                    expected_version in args[0],
                    "the version should default to a datetime string.")
                return

        self.fail("No checkinstall command was run.")

    @helpers.set_options(config_file="foo.json")
    def test_specified_config_file(self):
        ubuild_modules.runner.main()
        self.assert_opened_config_file("foo.json")

    @helpers.use_config({
        "module_import": "foo.bar.modules",
        "build_module": "foomodule",
    })
    def test_import_module(self):
        mock_module = mock.Mock()
        mock_registry = {"foomodule": mock_module}
        with mock.patch.dict(
                "ubuild_modules.registry._MODULE_REGISTRY", mock_registry):
            with mock.patch("importlib.import_module") as mock_import:
                ubuild_modules.runner.main()
                mock_import.assert_called_with("foo.bar.modules")

        self.assertTrue(mock_module.return_value.prep.called)
        self.assertTrue(mock_module.return_value.build.called)
        self.assertTrue(mock_module.return_value.cleanup.called)
