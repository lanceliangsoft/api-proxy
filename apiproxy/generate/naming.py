import re
import nltk
from nltk.tokenize import word_tokenize
from typing import List
from ..service.str_util import get_url_path


def guess_entity_name(method: str, url: str) -> str:
    ep_path = get_url_path(url)
    pieces = ep_path.split("/")
    words = []
    for piece in pieces[-2:]:
        words.extend(split_name(piece))
    tokens = word_tokenize(" ".join(words))
    tags = nltk.pos_tag(tokens)
    nouns = []
    verb = ""
    # found nouns in the last 2 segments of the url path.
    for word, attr in tags:
        if attr == "NN":
            nouns.append(word)
        elif attr == "NNS":
            nouns.append(singular_format(word))
        elif "VB" in attr:
            verb = word
    # prepend a verb if found.
    if verb != "":
        nouns.insert(0, verb)
        return "".join(word.capitalize() for word in nouns)
    else:
        return get_verb_from_method(method) + "".join(
            word.capitalize() for word in nouns
        )


def get_verb_from_method(method: str) -> str:
    if method == "GET":
        return "retrieve"
    elif method == "POST":
        return "create"
    elif method == "PUT":
        return "update"
    elif method == "DELETE":
        return "remove"
    else:
        return method.lower()


def split_name(name: str) -> List[str]:
    return re.split(r"_|-|(?<=[a-z0-9])(?=[A-Z])", name)


def pascal_case(name: str) -> str:
    return "".join(s.capitalize() for s in split_name(name))


def camel_case(name: str) -> str:
    words = split_name(name)
    return words[0].lower() + "".join(s.capitalize() for s in words[1:])


def snake_case(name: str) -> str:
    words = split_name(name)
    return "_".join(word.lower() for word in words)


def singular_format(word: str) -> str:
    return re.sub(r"((?<=s)e)?s$", "", word)
