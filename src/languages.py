import re


class BaseLanguage:
    name = "Base"
    extension = ""
    default_command = ""
    timeout = 10
    system_prompt = (
        "You are a helpful coding assistant. Fix the following error in the code."
    )

    def match_errors(self, stderr):
        raise NotImplementedError

    def get_suggestion(self, message):
        msg = message.lower()
        if "zero division" in msg or "zerodivisionerror" in msg:
            return "Check if the denominator can be zero before performing division."
        if "syntaxerror" in msg or "expected" in msg:
            return "Check for missing quotes, brackets, parentheses, or semicolons."
        if "not defined" in msg or "undeclared" in msg:
            return "Ensure the variable or function is spelled correctly and declared/imported."
        return "Review the code block around this line for logical or syntax issues."


class PythonLanguage(BaseLanguage):
    name = "Python"
    extension = ".py"
    default_command = "python"
    timeout = 10
    system_prompt = "You are a Python expert. Analyze the traceback, identify the bug, and provide the corrected code snippet."

    def match_errors(self, stderr):
        errors = []
        file_line_pattern = re.compile(r'File "(.*?)", line (\d+)(?:, in (.*?))?')
        matches = list(file_line_pattern.finditer(stderr))
        if not matches:
            return errors

        error_msg = "Runtime Exception"
        for line in stderr.splitlines():
            if ":" in line and not line.startswith(" ") and not line.startswith("File"):
                error_msg = line.strip()

        last_match = matches[-1]
        filepath, line_num, func = last_match.groups()
        errors.append(
            {
                "language": self.name,
                "file": filepath,
                "line": int(line_num),
                "col": 1,
                "message": error_msg,
                "system_prompt": self.system_prompt,
            }
        )
        return errors


class CLanguage(BaseLanguage):
    name = "C"
    extension = ".c"
    default_command = "gcc"
    timeout = 15
    system_prompt = "You are a C systems programming expert. Fix compilation errors, memory leaks, or syntax issues."

    def match_errors(self, stderr):
        errors = []
        pattern = re.compile(r"^(.*?):(\d+):(?:(\d+):)?\s*error:\s*(.*)$", re.MULTILINE)
        for match in pattern.finditer(stderr):
            filepath, line_num, col_num, message = match.groups()
            errors.append(
                {
                    "language": self.name,
                    "file": filepath,
                    "line": int(line_num),
                    "col": int(col_num) if col_num else 1,
                    "message": message.strip(),
                    "system_prompt": self.system_prompt,
                }
            )
        return errors


class JavaLanguage(BaseLanguage):
    name = "Java"
    extension = ".java"
    default_command = "javac"
    timeout = 15
    system_prompt = "You are a Java expert. Fix compilation or runtime exceptions adhering to Java standards."

    def match_errors(self, stderr):
        errors = []
        pattern = re.compile(r"^(.*?):(\d+):\s*error:\s*(.*)$", re.MULTILINE)
        for match in pattern.finditer(stderr):
            filepath, line_num, message = match.groups()
            errors.append(
                {
                    "language": self.name,
                    "file": filepath,
                    "line": int(line_num),
                    "col": 1,
                    "message": message.strip(),
                    "system_prompt": self.system_prompt,
                }
            )
        return errors


def get_all_languages():
    return [PythonLanguage(), CLanguage(), JavaLanguage()]


def get_language_by_extension(file_path):
    for lang in get_all_languages():
        if file_path.endswith(lang.extension):
            return lang
    return None
