import setuptools


setuptools.setup(
    name="ubuild",
    version="0.1.0",
    packages=["ubuild_modules"],
    entry_points={
        "console_scripts": [
            "ubuild = ubuild_modules.runner:main"
        ]
    })
