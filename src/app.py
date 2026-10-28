import shutil
import sys
import os
import subprocess
from exec import run_command
from parser import parse_and_process_errors, render_rust_style


def copy_to_clipboard(text):
    outcome = (
        "\n✨ success Copied system prompt, error details, and file context to clipboard!",
        f"\n⚠️ Failed to copy to clipboard automatically, Copy the following text:\n\n```\n{text}\n```\n",
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
    print("🚀 Run `python src/app.py --server` to chat with AI or inspect further.")


def check_server():
    if sys.argv[1] == "--server":
        return True
    return False


def check_dependencies():
    missing = []
    if shutil.which("streamlit") is None:
        missing.append("streamlit")
    if shutil.which("ollama") is None:
        missing.append("ollama")

    if missing:
        print(f"[Error]: Missing required system dependencies: {', '.join(missing)}")
        if "streamlit" in missing:
            print("  -> Install it via: pip install streamlit")
        if "ollama" in missing:
            print("  -> Install Ollama from: https://ollama.com/")
        sys.exit(1)


def run_streamlit_server():
    check_dependencies()

    server_path = os.path.join(os.path.dirname(__file__), "server.py")

    if not os.path.exists(server_path):
        print(f"[Error]: Could not find server script at {server_path}")
        sys.exit(1)

    print(f"[*] Starting DebugBuddy UI via Streamlit...")
    try:
        # Run streamlit as a subprocess
        subprocess.run(["streamlit", "run", server_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[Error]: Streamlit server exited with code {e.returncode}")
    except KeyboardInterrupt:
        print("\n[*] Shutting down DebugBuddy AI Assistant server.")


def main():
    if check_server():
        run_streamlit_server()
        return

    output, err = run_command(sys.argv)

    if err is None:
        if output is not None:
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
