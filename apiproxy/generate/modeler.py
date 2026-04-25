import json
from typing import Any, Dict, List, Tuple, Type, TypeAlias
from .naming import pascal_case, singular_format

ValueType: TypeAlias = "ClassDef | ListDef | str"


class FieldDef:
    name: str
    type: ValueType

    def __init__(self, name: str, type: ValueType):
        self.name = name
        self.type = type


class ClassDef:
    name: str
    fields: List[FieldDef]

    def __init__(self, name: str):
        self.name = name
        self.fields = []

    def __str__(self) -> str:
        return f"class {self.name}"


class ListDef:
    elem_type: ValueType

    def __init__(self, elem_type: ValueType):
        self.elem_type = elem_type

    def __str__(self) -> str:
        return f"list[{self.elem_type}]"


def merge_types(type1: ValueType, type2: ValueType) -> ValueType:
    if str(type1) == str(type2):
        return type1
    elif type1 == "":
        return type2
    else:
        return "*"


class Modeler:
    def __init__(self):
        self._classes: Dict[str, ClassDef] = {}
        self._root: ValueType = "*"

    def analyze(self, payload: bytes, class_name: str):
        obj = json.loads(payload.decode())
        self._root = self.analyze_value(obj, class_name)

    def analyze_value(self, value: Any, name: str) -> ValueType:
        if value is None:
            return "None"
        if isinstance(value, str):
            return "String"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, list):
            return self.analyze_list(value, name)  # Simplified list type
        elif isinstance(value, dict):
            return self.analyze_object(value, name)
        else:
            raise TypeError(f"Unsupported type of json field {value}")

    def analyze_object(self, obj: dict, name: str) -> ClassDef:
        class_def = ClassDef(pascal_case(name))
        for key, value in obj.items():
            field_type = self.analyze_value(value, key)
            class_def.fields.append(FieldDef(name=key, type=field_type))

        self._classes[class_def.name] = class_def
        return class_def

    def analyze_list(self, lst: list, name: str) -> ListDef:
        name = singular_format(name)
        elem_type = ""
        for item in lst:
            type = self.analyze_value(item, name)
            elem_type = merge_types(elem_type, type)

        return ListDef(elem_type)

    def get_root(self) -> ValueType:
        return self._root

    def get_classes(self) -> List[ClassDef]:
        return [x for x in self._classes.values()]
    
