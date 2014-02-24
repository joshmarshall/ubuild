import json
import mock
from tests import helpers

from ubuild_modules import virtualenv_module
import ubuild_modules.runner


class TestVirtualEnvModuleWithRunner(helpers.RunnerTestCase):

    @helpers.set_options(version="1234", config_file="foo.json")
    @helpers.use_config(helpers.VIRTUALENV_CONFIG)
    def test_virtualenv_module(self):

        expected_config = json.dumps({
            "steps": [{
                "name": "virtualenv.execute",
                "virtualenv_path": "/opt/venv/virtual",
                "requirements_files": ["requirements.txt", "extra-reqs.txt"],
                "requirements_params": ["--allow-all-external"]
            }]
        })

        with mock.patch("sys.argv") as mock_argv:
            mock_argv.__getitem__.return_value = "/usr/bin/ubuild"
            with mock.patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                mock_file = mock_temp_file.return_value.__enter__.return_value
                mock_file.name = "foobar.json"
                mock_temp_file.return_value.__enter__.name = "foobar.json"

                ubuild_modules.runner.main()

                mock_file.write.assert_called_with(expected_config)
                mock_file.flush.assert_called_with()

        self.assert_calls([
            "apt-get update",
            "apt-get install -y checkinstall libcurl python-dev "
            "python-setuptools",
            "easy_install pip",
            "pip install virtualenv",
            "checkinstall --showinstall=no -y --requires='libcurl' "
            "--pkgname='foojson' --provides='foojson' --nodoc "
            "--deldoc=yes --deldesc=yes --delspec=yes "
            "--backup=no --pkgversion='1234' "
            "/usr/bin/ubuild --config 'foobar.json'"
        ])

    def test_virtualenv_build(self):
        config = {
            "virtualenv_path": "/opt/venv/virtual",
            "requirements_files": ["requirements.txt", "extra-reqs.txt"],
            "requirements_params": ["--allow-all-external"]
        }

        commands = []

        def execute(command):
            commands.append(command)

        virtualenv_module.execute_virtualenv({}, config, execute)
        self.assertEqual([
            "mkdir -p /opt/venv",
            "virtualenv /opt/venv/virtual --always-copy",
            #"source /opt/venv/virtual/activate",
            "/opt/venv/virtual/bin/pip install -I "
            "-r requirements.txt -r extra-reqs.txt --allow-all-external",
            "/opt/venv/virtual/bin/python setup.py install"
        ], commands)
