from datetime import datetime
import mock
import subprocess
import unittest

from ubuild_modules.helpers import generate_datetime_version, execute
from ubuild_modules.helpers import update_command


class TestHelpers(unittest.TestCase):

    def test_generate_datetime_version(self):
        start = datetime.utcnow().strftime("%Y%m%d.%H%M%S")
        version = generate_datetime_version()
        end = datetime.utcnow().strftime("%Y%m%d.%H%M%S")
        self.assertTrue(float(start) <= float(version) <= float(end))

    @mock.patch("subprocess.Popen")
    def test_execute(self, mock_popen):

        def side_effect(command, shell, stdout, stderr):
            self.assertEqual("foobar thing", command)
            self.assertTrue(shell)
            self.assertEqual(subprocess.PIPE, stdout)
            self.assertEqual(subprocess.STDOUT, stderr)
            result = mock.Mock()
            result.wait.return_value = 0
            result.stdout.read.return_value = "FOOBAR!"
            return result

        mock_popen.side_effect = side_effect

        output = execute("foobar thing")
        self.assertEqual("FOOBAR!", output)

    @mock.patch("subprocess.Popen")
    def test_execute_fails(self, mock_popen):
        mock_popen.return_value.wait.return_value = 1
        with self.assertRaises(RuntimeError):
            execute("whatever")

    @mock.patch("subprocess.Popen")
    def test_execute_escapes_quotes(self, mock_popen):
        mock_popen.return_value.wait.return_value = 0
        execute("mycommand -a {arg} {}", "; rm;", arg="'quote tacular'")
        mock_popen.assert_called_with(
            "mycommand -a ''\"'\"'quote tacular'\"'\"'' '; rm;'",
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    @mock.patch.dict("os.environ", {"PATH": "/tmp"})
    def test_update_command(self):
        context = {"foo": "bar", "bar": "baz"}
        command = "do $C:FOO with $C:BAR and $PATH"
        output = update_command(context, command)
        self.assertEqual("do bar with baz and /tmp", output)
