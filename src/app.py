import shutil
import sys
import subprocess
from exec import run_command
from parser import parse_and_process_errors, render_rust_style


def copy_to_clipboard(text):
    outcome = (
        f"\n✨ success Copied system prompt, error details, and file context to clipboard!",
        "\n⚠️ Failed to copy to clipboard automatically.",
    )
    try:
        if sys.platform == "darwin":
            subprocess.run("pbcopy", input=text, text=True, check=True)
            print(outcome[0])
            return

        if sys.platform.startswith("win"):
            subprocess.run("clip", input=text, text=True, check=True)
            print(outcome[0])
            return

        if shutil.which("wl-copy"):
            subprocess.run(["wl-copy"], input=text, text=True, check=True)
            print(outcome[0])
            return

        if shutil.which("xclip"):
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text,
                text=True,
                check=True,
            )
            print(outcome[0])
        else:
            print(outcome[1])
    except Exception:
        print(outcome[1])


def copy_payload(structured_errors):
    payload_lines = []
    for e in structured_errors:
        payload_lines.append(f"System Prompt: {e['system_prompt']}")
        payload_lines.append(f"Error: {e['message']}")
        payload_lines.append(f"File: {e['file']} (Line {e['line']})")
        if e["context"]:
            ctx_str = "\n".join([f"{ln}: {txt}" for ln, txt in e["context"]])
            payload_lines.append(f"Context:\n{ctx_str}")
    return "\n".join(payload_lines)


def print_structured_error(structured_errors):
    print(f"\nFound {len(structured_errors)} diagnostic(s):")
    for err_obj in structured_errors:
        render_rust_style(err_obj)


def print_run_server():
    print("🚀 Run `streamlit run src/server.py` to chat with AI or inspect further.")


def main():
    output, err = run_command()

    if err is None:
        print(output)
        return

    structured_errors = parse_and_process_errors(err)

    if not structured_errors:
        print(f"\n[Raw Error Output]\n{err}")
    else:
        print_structured_error(structured_errors)
        payload = copy_payload(structured_errors)
        copy_to_clipboard(payload)

    print_run_server()


if __name__ == "__main__":
    main()
