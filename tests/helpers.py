import functools
import json
import mock
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


def use_config(config):
    def wrapper(method):
        @functools.wraps(method)
        def wrapper_method(test_case):
            test_case._ubuild_config = config
            return method(test_case)
        return wrapper_method
    return wrapper


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
        self._open_patcher = mock.patch("__builtin__.open")
        self._call_patcher = mock.patch("subprocess.call")
        self._args_patcher = mock.patch("optparse.OptionParser.parse_args")
        self._exists_patcher = mock.patch("os.path.exists")

        self._mock_file = mock.MagicMock(spec=file)
        self._mock_file.__enter__.return_value.read.side_effect = \
            lambda: json.dumps(self._ubuild_config)

        self._mock_open = self._open_patcher.start()
        self._mock_open.return_value = self._mock_file
        self._mock_call = self._call_patcher.start()
        self._mock_call.return_value = 0

        self._mock_options = mock.Mock()
        self._mock_options.version = None
        self._mock_options.config_file = None
        self._mock_options.build_module = False

        self._mock_args = self._args_patcher.start()
        self._mock_args.return_value = (self._mock_options, None)

        self._mock_exists = self._exists_patcher.start()
        self._mock_exists.return_value = True

    def tearDown(self):
        super(RunnerTestCase, self).tearDown()
        self._open_patcher.stop()
        self._call_patcher.stop()
        self._args_patcher.stop()
        self._exists_patcher.stop()

    def assert_calls(self, expected_calls):
        self.assertEqual(len(expected_calls), len(self._mock_call.mock_calls))
        for i in range(len(expected_calls)):
            self.assertEqual(
                mock.call(expected_calls[i], shell=True),
                self._mock_call.mock_calls[i])

    @property
    def calls(self):
        # syntactical sugarifying
        return self._mock_call.mock_calls

    def assert_opened_config_file(self, path):
        self._mock_open.assert_called_with(path)
