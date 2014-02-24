from datetime import datetime
import os
import subprocess


def generate_datetime_version():
    return datetime.utcnow().strftime("%Y%m%d.%H%M%S")


def execute(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = process.wait()
    stdout = process.stdout.read()
    if result != 0:
        raise RuntimeError("Could not execute command (%d): %s\n%s" % (
            result, command, stdout))
    return stdout


def update_command(context, command):
    for key, value in context.items():
        command = command.replace("$C:%s" % (key.upper()), value)
    for key, value in os.environ.items():
        command = command.replace("$%s" % (key.upper()), value)
    return command
