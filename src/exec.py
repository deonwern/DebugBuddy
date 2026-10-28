import os
import subprocess
import sys
from languages import get_lang_by_extension


def exec_command(command, timeout=10):
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True,
        )
        return (result.stdout, None)
    except subprocess.TimeoutExpired as e:
        return (
            None,
            f"Command timed out after {timeout} seconds.",
        )
    except subprocess.CalledProcessError as e:
        return (None, e.stderr)


def get_data_by_extention(args):
    for arg in args:
        if os.path.isfile(arg):
            lang = get_lang_by_extension(arg)
            if lang is not None:
                return (f"{lang.default_command(arg)}", lang.name, lang.timeout)
    return (None, None, None)


def check_args(args):
    if len(args) >= 2:
        return False
    return True


def run_command(args):
    if check_args(args):
        print("Usage: python error_handler.py <file name>")
        return (None, None)

    ext_data = get_data_by_extention(args[1])
    if ext_data is None:
        print("Error: Unsupported file extension or invalid file provided.")
        return (None, None)

    command, name, timeout = ext_data

    print(f"Language detected as: {name}")
    print(f"Executing: {command}")

    if command is not None:
        if timeout is None:
            timeout = 10
        output, err = exec_command(command, timeout=timeout)
        if err is not None:
            return (None, err)
        else:
            return (output, None)

    return (None, None)
