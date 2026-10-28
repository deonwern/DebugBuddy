import os
from languages import get_all_languages

RED = "\033[1;31m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def extract_code_context(filepath, line_num, context_lines=2):
    """Extracts target line and preceding/succeeding lines for context."""
    snippet = []
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                start = max(0, line_num - 1 - context_lines)
                end = min(len(lines), line_num + 1)
                for idx in range(start, end):
                    snippet.append((idx + 1, lines[idx].rstrip()))
    except Exception:
        pass
    return snippet


def parse_and_process_errors(stderr_output):
    if not stderr_output:
        return []

    all_errors = []
    for lang_class in get_all_languages():
        parser = lang_class()  # Instantiate the language class
        errors = parser.match_errors(stderr_output)
        for err in errors:
            # Suggestion is already populated by match_errors via resolve_suggestion
            err["context"] = extract_code_context(err["file"], err["line"])
            all_errors.append(err)

    return all_errors


def render_rust_style(error):
    """Renders a dead-simple, beautiful Rust-style card with full-line error highlighting."""
    filepath = error["file"]
    line_num = error["line"]
    col_num = error["col"]
    msg = error["message"]
    lang = error["language"]

    print(f"\n{RED}error[{lang}]{RESET}: {BOLD}{msg}{RESET}")
    print(f"  {CYAN}-->{RESET} {filepath}:{line_num}:{col_num}")
    print(f"   {CYAN}|{RESET}")

    if error["context"]:
        for l_num, text in error["context"]:
            if l_num == line_num:
                # Highlight the entire error line for instant visibility
                print(
                    f"{l_num:3d} {CYAN}|{RESET} {RED}{BOLD}{text}{RESET}  {RED}← [ERROR HERE]{RESET}"
                )
            else:
                print(f"{l_num:3d} {CYAN}|{RESET} {DIM}{text}{RESET}")
    else:
        print(f"    {CYAN}|{RESET} [Source code snippet unavailable]")

    print(f"   {CYAN}|{RESET}")
    if error.get("suggestion"):
        print(f"    {YELLOW}= note{RESET}: {error['suggestion']}")
