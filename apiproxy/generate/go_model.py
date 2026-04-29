
from typing import List

from .naming import camel_case
from .modeler import ClassDef, ListDef, Modeler, ValueType
from ..service.models import GeneratedFile
from ..service.str_util import trim_indent

async def generate_go_models(
    json_payload: str, root_element: str
) -> List[GeneratedFile]:
    models: List[str] = [trim_indent(
        """import (
            "encoding/json"
            "fmt"
        )""")]
    modeler = Modeler()

    modeler.analyze(json_payload.encode(), root_element)
    for class_def in modeler.get_classes():
        models.append(generate_go_model(class_def))
    return [
        GeneratedFile(
            file_name="models.go",
            content = "\n\n".join(models)
        )
    ]

def generate_go_model(class_def: ClassDef) -> str:
    model = f"type {class_def.name} struct " "{\n"
    for field in class_def.fields:
        field_name = camel_case(field.name)
        field_type = to_go_type(field.type)
        model += f"    {field_name} {field_type} `json:\"{field.name}\"`\n"
    model += "}\n"

    return model


def to_go_type(type: ValueType) -> str:
    if isinstance(type, ClassDef):
        return type.name
    elif isinstance(type, ListDef):
        return f"[]{to_go_type(type.elem_type)}"
    elif type == 'String':
        return 'string'
    elif type == 'boolean':
        return 'bool'
    else:
        return str(type)

