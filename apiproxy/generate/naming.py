import re
from typing import List
from ..service.str_util import split_path


def guess_entity_name(method: str, url: str) -> str:
    base_path, ep_path = split_path(url)
    return ep_path


def split_name(name: str) -> List[str]:
    return re.split(r"_|-|(?<=[a-z0-9])(?=[A-Z])", name)


def pascal_case(name: str) -> str:
    return "".join([s.capitalize() for s in split_name(name)])


def camel_case(name: str) -> str:
    segs = split_name(name)
    return segs[0].lower() + "".join([s.capitalize() for s in segs[1:]])


def singular_format(word: str) -> str:
    return re.sub(r'((?<=s)e)?s$', '', word)
