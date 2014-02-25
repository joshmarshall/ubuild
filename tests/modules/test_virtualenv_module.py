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
                "requirements_params": ["--allow-all-external"],
                "download_path": None
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
            "checkinstall --showinstall=no -y --requires=libcurl "
            "--pkgname=foojson --provides=foojson --nodoc "
            "--deldoc=yes --deldesc=yes --delspec=yes "
            "--backup=no --pkgversion=1234 "
            "'/usr/bin/ubuild --config foobar.json'"
        ])

    def test_virtualenv_build_with_download(self):
        config = {
            "project_name": "ubuild",
            "virtualenv_path": "/opt/venv/virtual",
            "requirements_files": ["foo.txt", "bar.txt"],
            "requirements_params": ["--allow-all-external"],
            "download_path": "/tmp/download"
        }

        virtualenv_module.build_virtualenv({}, config, self.execute)

        # make sure the last command is checkinstall...
        self.assertTrue(self.commands.pop(-1).startswith("checkinstall "))

        self.assertEqual([
            "mkdir -p /tmp/download",
            "pip install --download /tmp/download -r foo.txt -r bar.txt "
            "--allow-all-external"
        ], self.commands)

        self.commands = []
        virtualenv_module.execute_virtualenv({}, config, self.execute)

        self.assertEqual([
            "mkdir -p /opt/venv",
            "virtualenv /opt/venv/virtual --always-copy",
            "/opt/venv/virtual/bin/pip install -I --no-index "
            "--find-links file:///tmp/download -r foo.txt -r bar.txt "
            "--allow-all-external",
            "/opt/venv/virtual/bin/python setup.py install"
        ], self.commands)

    def test_virtualenv_build(self):
        config = {
            "virtualenv_path": "/opt/venv/virtual",
            "requirements_files": ["requirements.txt", "extra-reqs.txt"],
            "requirements_params": ["--allow-all-external"]
        }

        virtualenv_module.execute_virtualenv({}, config, self.execute)
        self.assertEqual([
            "mkdir -p /opt/venv",
            "virtualenv /opt/venv/virtual --always-copy",
            "/opt/venv/virtual/bin/pip install -I "
            "-r requirements.txt -r extra-reqs.txt --allow-all-external",
            "/opt/venv/virtual/bin/python setup.py install"
        ], self.commands)

    def test_virtualenv_build_simple_requirements(self):
        config = {
            "virtualenv_path": "/opt/venv",
            "project_name": "foobar",
            "requirements_files": [],
            "download_path": "/tmp/download"
        }
        virtualenv_module.build_virtualenv({}, config, self.execute)
        self.assertTrue(True, "Executed without issue.")
