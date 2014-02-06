from tests import helpers
import ubuild_modules.runner


class TestVirtualEnvModuleRunner(helpers.RunnerTestCase):

    _ubuild_config = helpers.VIRTUALENV_CONFIG

    @helpers.set_options(version="1234", config_file="foo.json")
    def test_virtualenv_module(self):
        ubuild_modules.runner.main()
        self.assert_calls([
            "apt-get update",
            "apt-get install -y checkinstall libcurl python-dev "
            "python-setuptools",
            "easy_install pip",
            "pip install virtualenv",
            "checkinstall --showinstall=no -y --requires='libcurl' "
            "--pkgname='foojson' --provides='foojson' --nodoc "
            "--deldoc=yes --deldesc=yes --delspec=yes "
            "--pkgversion='1234' ubuild --build_module "
            "--version=1234 --config=foo.json"
        ])

    @helpers.set_options(build_module=True)
    def test_virtualenv_build(self):
        ubuild_modules.runner.main()
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
