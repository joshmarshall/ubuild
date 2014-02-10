from datetime import datetime
import subprocess


def generate_datetime_version():
    return datetime.utcnow().strftime("%Y%m%d.%H%M%S")


def execute(command):
    result = subprocess.call(command, shell=True)
    if result != 0:
        raise RuntimeError("Could not execute command (%d): %s" % (
            result, command))
