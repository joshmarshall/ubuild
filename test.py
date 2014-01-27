import datetime
import mock
import ubuild
import unittest

_FAKE_CONFIG = """{
    "name": "foobar",
    "build_requires": ["package"],
    "requires": ["package"],
    "build_command": "make install"
}"""


class TestuBuild(unittest.TestCase):

    def setUp(self):
        self._open_patcher = mock.patch("__builtin__.open")
        self._call_patcher = mock.patch("subprocess.call")
        self._args_patcher = mock.patch("optparse.OptionParser.parse_args")
        self._exists_patcher = mock.patch("os.path.exists")

        self._mock_file = mock.MagicMock(spec=file)
        self._mock_file.__enter__.return_value.read.return_value = _FAKE_CONFIG

        self._mock_open = self._open_patcher.start()
        self._mock_open.return_value = self._mock_file
        self._mock_call = self._call_patcher.start()
        self._mock_call.return_value = 0

        self._mock_options = mock.Mock()
        self._mock_options.version = None
        self._mock_options.config_file = None

        self._mock_args = self._args_patcher.start()
        self._mock_args.return_value = (self._mock_options, None)

        self._mock_exists = self._exists_patcher.start()
        self._mock_exists.return_value = True

    def tearDown(self):
        self._open_patcher.stop()
        self._call_patcher.stop()
        self._args_patcher.stop()
        self._exists_patcher.stop()

    def test_main(self):
        self._mock_options.version = "1234"

        ubuild.main()

        self._mock_open.assert_called_with(".ubuild.json")
        self._mock_call.assert_has_calls([
            mock.call("apt-get update", shell=True),
            mock.call(u"apt-get install -y checkinstall package", shell=True),
            mock.call(
                u"checkinstall --showinstall=no -y --requires='package' "
                "--pkgname='foobar' --provides='foobar' --nodoc --deldoc=yes "
                "--deldesc=yes --delspec=yes --pkgversion='1234' "
                "make install", shell=True)
        ])

    def test_default_version(self):
        ubuild.main()

        for name, args, kwargs in self._mock_call.mock_calls:
            if args[0].startswith("checkinstall"):
                now = datetime.datetime.utcnow().strftime("%Y%m%d.%H%M%S")
                expected_version = "--pkgversion='%s'" % (now)
                self.assertTrue(
                    expected_version in args[0],
                    "the version should default to a datetime string.")
                return

        self.fail("No checkinstall command was run.")

    def test_specified_config_file(self):
        self._mock_options.config_file = "foo.json"
        ubuild.main()

        self._mock_open.assert_called_with("foo.json")
