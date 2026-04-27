import re
from datetime import datetime
from typing import Tuple


def trim_indent(text: str) -> str:
    lines = text.splitlines()
    if len(lines) > 1:
        last_line = lines[-1:][0]
        leading_spaces = get_leading_spaces(last_line)
        for i in range(0, len(lines)):
            if lines[i].startswith(leading_spaces):
                lines[i] = lines[i][len(leading_spaces) :]
        return "\n".join(lines)
    else:
        return text


def get_leading_spaces(line: str) -> str:
    if m := re.search(r"^\s+", line):
        return m.group(0)
    else:
        return ""


def split_path(url: str) -> Tuple[str, str]:
    if m := re.search(r"^http[s]?://([^/]+)(/api(?:/v\d+)?)?(/?[^\&]*)(&.*)?$", url):
        return m.group(2) or "", m.group(3)
    elif m := re.search(r"^(/api(?:/v\d+)?)?(/[^\&]*)(&.*)?$", url):
        return m.group(2) or "", m.group(3)
    else:
        return "", url


def get_url_path(url: str) -> str:
    if m := re.search(r"^http[s]?://([^/]+)([^\&]*)(&.*)?$", url):
        return m.group(2)
    elif m := re.search(r"^(/[^\&]*)(&.*)?$", url):
        return m.group(1)
    else:
        return url


def parse_datetime(iso_date: str | None) -> datetime | None:
    if iso_date is None:
        return None
    return datetime.fromisoformat(iso_date)
