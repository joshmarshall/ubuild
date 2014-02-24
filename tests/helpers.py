import functools
import json
import mock
from StringIO import StringIO
import subprocess
import unittest


SIMPLE_CONFIG = {
    "steps": [
        {
            "name": "checkinstall.prepare",
            "build_requires": ["package"],
        }, {
            "name": "checkinstall.build",
            "project_name": "foobar",
            "project_requires": ["package"],
            "build_command": "make install"
        }
    ]
}


VIRTUALENV_CONFIG = {
    "steps": [
        {
            "name": "virtualenv.prepare",
            "build_requires": ["libcurl"]
        },
        {
            "name": "virtualenv.build",
            "project_name": "foojson",
            "project_requires": ["libcurl"],
            "virtualenv_path": "/opt/venv/virtual",
            "requirements_files": ["requirements.txt", "extra-reqs.txt"],
            "requirements_params": ["--allow-all-external"]
        }
    ]
}


class MockProcess(object):

    def __init__(self, return_code, stdout):
        self._return_code = return_code
        self.stdout = StringIO(stdout)

    def wait(self):
        return self._return_code


class use_config(object):

    def __init__(self, config):
        self._config = config

    def __call__(self, method):
        @functools.wraps(method)
        def wrapper_method(test_case):
            with self as mocker:
                test_case.mock_config = mocker
                return method(test_case)
        return wrapper_method

    def __enter__(self):
        self._open_patcher = mock.patch("__builtin__.open")
        self._mock_file = mock.MagicMock(spec=file)
        self._mock_file.__enter__.return_value.read.side_effect = \
            lambda: json.dumps(self._config)

        self._mock_open = self._open_patcher.start()
        self._mock_open.return_value = self._mock_file
        return self

    def __exit__(self, *args, **kwargs):
        self._open_patcher.stop()

    def assert_opened_config_file(self, path):
        self._mock_open.assert_called_with(path)


def set_options(**kwargs):
    def wrapper(method):
        @functools.wraps(method)
        def wrapper_method(test_case):
            for option_name, option_value in kwargs.items():
                setattr(test_case._mock_options, option_name, option_value)
            return method(test_case)
        return wrapper_method
    return wrapper


class RunnerTestCase(unittest.TestCase):

    def setUp(self):
        super(RunnerTestCase, self).setUp()
        # this should probably be deconstructed into multiple mixins...
        self._popen_patcher = mock.patch("subprocess.Popen")
        self._args_patcher = mock.patch("optparse.OptionParser.parse_args")
        self._exists_patcher = mock.patch("os.path.exists")

        self._mock_popen = self._popen_patcher.start()
        self._mock_popen.return_value = MockProcess(0, "")

        self._mock_options = mock.Mock()
        self._mock_options.version = None
        self._mock_options.config_file = None
        self._mock_options.build_module = False
        self._mock_options.step_name = None
        self._mock_options.step_config = None

        self._mock_args = self._args_patcher.start()
        self._mock_args.return_value = (self._mock_options, None)

        self._mock_exists = self._exists_patcher.start()
        self._mock_exists.return_value = True

    def tearDown(self):
        super(RunnerTestCase, self).tearDown()
        self._popen_patcher.stop()
        self._args_patcher.stop()
        self._exists_patcher.stop()

    def assert_calls(self, expected_calls):
        self.assertEqual(len(expected_calls), len(self._mock_popen.mock_calls))
        for i in range(len(expected_calls)):
            self.assertEqual(
                mock.call(
                    expected_calls[i], shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT),
                self._mock_popen.mock_calls[i])

    @property
    def calls(self):
        # syntactical sugarifying
        return self._mock_popen.mock_calls


class mock_import(object):

    def __init__(self, registrations):
        self._registrations = registrations

    def _import(self, import_module):
        if import_module not in self._registrations:
            # this could get confusing...
            return mock.Mock(register=lambda x: None)
        return mock.Mock(register=self._registrations[import_module])

    def __enter__(self):
        self._mock_patcher = mock.patch("importlib.import_module")
        self._mock_import = self._mock_patcher.start()
        self._mock_import.side_effect = self._import

    def __exit__(self, *args, **kwargs):
        self._mock_patcher.stop()
