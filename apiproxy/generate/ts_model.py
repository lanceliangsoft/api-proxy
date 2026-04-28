from typing import List

from .modeler import ClassDef, ListDef, Modeler, ValueType
from ..service.str_util import trim_indent
from ..service.models import GeneratedFile


def generate_ts_model(class_def: ClassDef) -> GeneratedFile:

    return GeneratedFile(
        file_name=f"src/model/{class_def.name}.ts",
        content=generate_ts_class(class_def),
    )


async def generate_typescript_models(
    json_payload: str, root_element: str
) -> List[GeneratedFile]:
    files: List[GeneratedFile] = []
    modeler = Modeler()

    modeler.analyze(json_payload.encode(), root_element)
    for class_def in modeler.get_classes():
        files.append(generate_ts_model(class_def))
    return files


def generate_ts_class(class_def: ClassDef) -> str:
    # to map non-ts convention json field name such as 'hello-world'.
    field_decls = [
        f"{field.name}: {to_ts_type(field.type)} | undefined,"
        for field in class_def.fields
    ]

    return trim_indent(f"""
        export interface {class_def.name} {{
            {"\n            ".join(field_decls)}
        }}
        """)


def to_ts_type(type: ValueType) -> str:
    if isinstance(type, ClassDef):
        return type.name
    elif isinstance(type, ListDef):
        return "Array<" + to_ts_type(type.elem_type) + ">"
    elif type == "String":
        return "string"
    elif type == "int":
        return "number"
    elif type == "double":
        return "number"
    elif type == "None":
        return "null"
    elif type == "*":
        return "any"
    else:
        return str(type)
