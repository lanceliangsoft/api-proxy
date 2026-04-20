import re


def trim_indent(text: str) -> str:
    lines = text.splitlines()
    if len(lines) > 1:
        last_line = lines[-1:][0]
        leading_spaces = get_leading_spaces(last_line)
        for i in range(0, len(lines)):
            if lines[i].startswith(leading_spaces):
                lines[i] = lines[i][len(leading_spaces):]
        return "\n".join(lines)
    else:
        return text


def get_leading_spaces(line: str) -> str:
    if m := re.search(r"^\s+", line):
        return m.group(0)
    else:
        return ""
