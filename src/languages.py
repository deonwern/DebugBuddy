import re


class BaseLanguage:
    name = "Base"
    default_command = lambda self, x: "Language not defined!"
    timeout = 10
    system_prompt = (
        "You are a helpful coding assistant. Fix the following error in the code."
    )

    # Fallback single pattern or mapping of patterns
    error_pattern = None
    error_patterns = (
        []
    )  # List of tuples/dicts: (regex_pattern, message_extractor_func_or_index)
    get_suggestion = {}

    def resolve_suggestion(self, message: str) -> str:
        """Finds a matching suggestion from the class dictionary map."""
        msg_lower = message.lower()
        for keyword, suggestion in self.get_suggestion.items():
            if keyword.lower() in msg_lower:
                return suggestion
        return ""

    def _extract_raw_errors(self, stderr: str) -> list:
        """Parses stderr using either error_patterns maps or single error_pattern."""
        raw_errors = []

        # 1. Check if the language defines a specialized error_patterns map
        if self.error_patterns:
            for pattern_str, msg_resolver in self.error_patterns:
                for match in re.finditer(pattern_str, stderr, re.MULTILINE):
                    err_data = msg_resolver(match, stderr)
                    if err_data:
                        raw_errors.append(err_data)
            if raw_errors:
                return raw_errors

        # 2. Fallback to standard single error_pattern
        if not self.error_pattern:
            return []

        for match in re.finditer(self.error_pattern, stderr, re.MULTILINE):
            groups = match.groups()
            if len(groups) >= 4:
                filepath, line_num, col_num, message = groups[:4]
                col = int(col_num) if col_num else 1
            elif len(groups) == 3:
                filepath, line_num, message = groups
                col = 1
            else:
                continue

            raw_errors.append(
                {
                    "file": filepath,
                    "line": int(line_num),
                    "col": col,
                    "message": message.strip(),
                }
            )

        return raw_errors

    def _format_error(self, err: dict) -> dict:
        """Enriches raw error blocks with standard metadata and suggestions."""
        msg = err.get("message", "")
        return {
            "language": self.name,
            "file": err.get("file"),
            "line": err.get("line"),
            "col": err.get("col", 1),
            "message": msg,
            "system_prompt": self.system_prompt,
            "suggestion": self.resolve_suggestion(msg),
        }

    def match_errors(self, stderr: str) -> list:
        """Extracts, processes, and formats errors."""
        return [self._format_error(err) for err in self._extract_raw_errors(stderr)]


class PythonLanguage(BaseLanguage):
    name = "Python"
    default_command = lambda self, x: f"python {x}"
    timeout = 10
    system_prompt = "You are a Python expert. Analyze the traceback, identify the bug, and provide the corrected code snippet."

    get_suggestion = {
        "zerodivisionerror": "Check if the denominator can be zero before performing division.",
        "syntaxerror": "Check for missing quotes, brackets, parentheses, or semicolons.",
        "nameerror": "Ensure the variable or function is spelled correctly and declared/imported.",
    }

    # Declarative regex map for Python tracebacks
    error_patterns = [
        (
            r'File "(.*?)", line (\d+)(?:, in (.*?))?',
            lambda match, stderr: {
                "file": match.group(1),
                "line": int(match.group(2)),
                "col": 1,
                "message": next(
                    (
                        line.strip()
                        for line in stderr.splitlines()
                        if ":" in line
                        and not line.startswith(" ")
                        and not line.startswith("File")
                    ),
                    "Runtime Exception",
                ),
            },
        )
    ]


class CLanguage(BaseLanguage):
    name = "C"
    default_command = lambda self, x: f"gcc {x} && ./a.out"
    timeout = 15
    system_prompt = ""
    error_pattern = r"^(.*?):(\d+):(?:(\d+):)?\s*error:\s*(.*)$"

    get_suggestion = {
        "undeclared": "Ensure the variable or function is declared or included via headers.",
        "syntax error": "Check for missing semicolons, braces, or incorrect syntax.",
    }


class JavaLanguage(BaseLanguage):
    name = "Java"
    default_command = lambda self, x: f"java {x}"
    timeout = 15
    system_prompt = "You are a Java expert. Fix compilation or runtime exceptions adhering to Java standards."
    error_pattern = r"^(.*?):(\d+):\s*error:\s*(.*)$"

    get_suggestion = {
        "cannot find symbol": "Ensure variables, methods, or classes are declared and imported correctly.",
        "syntax error": "Check for missing semicolons, brackets, or parentheses.",
    }


lang_map = {
    ".py": PythonLanguage,
    ".c": CLanguage,
    ".java": JavaLanguage,
}


def get_all_languages():
    return set(lang_map.values())


def get_lang_by_extension(file_path):
    extension = f".{file_path.split(".")[-1]}"
    if extension in lang_map:
        return lang_map[extension]()
    else:
        return None
