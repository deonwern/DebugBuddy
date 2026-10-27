import subprocess
import sys
from languages import get_language_by_extension


def exec_command(command, target_file=None):
    timeout = 10
    if target_file:
        lang = get_language_by_extension(target_file)
        if lang:
            timeout = lang.timeout

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
    except subprocess.CalledProcessError as e:
        return (None, e.stderr)
    except subprocess.TimeoutExpired as e:
        err_msg = (
            e.stderr if e.stderr else f"Command timed out after {timeout} seconds."
        )
        return (None, err_msg)


def run_command():
    if len(sys.argv) < 2:
        return (None, "Usage: python error_handler.py <command>")

    command = " ".join(sys.argv[1:])

    target_file = None
    for arg in sys.argv[1:]:
        if any(arg.endswith(ext) for ext in [".py", ".c", ".java"]):
            target_file = arg
            break

    output, err = exec_command(command, target_file)
    if err is not None:
        return (None, err)
    else:
        return (output, None)
