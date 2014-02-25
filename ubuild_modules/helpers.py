from datetime import datetime
import sys
# this is shlex.quote in 3.3
from pipes import quote
import os
import subprocess

from ubuild_modules.logger import LOGGER


def generate_datetime_version():
    return datetime.utcnow().strftime("%Y%m%d.%H%M%S")


def execute(command, *args, **kwargs):
    positional_replacements = [quote(arg) for arg in args]
    keyword_replacements = dict([(k, quote(v)) for k, v in kwargs.items()])
    command = command.format(*positional_replacements, **keyword_replacements)
    LOGGER.info("Running command: {}".format(command))
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = []
    for line in iter(process.stdout.readline, ''):
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()
        output.append(line)

    result = process.wait()
    output = "\n".join(output)
    if result != 0:
        raise RuntimeError(
            "Could not execute command ({}): {}\n{}".format(
                result, command, output))
    return output


def update_command(context, command):
    for key, value in context.items():
        command = command.replace("$C:{}".format(key.upper()), value)
    for key, value in os.environ.items():
        command = command.replace("${}".format(key.upper()), value)
    return command
