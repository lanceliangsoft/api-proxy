
from typing import List

from .naming import snake_case
from .modeler import ClassDef, ListDef, Modeler, ValueType
from ..service.models import GeneratedFile
from ..service.str_util import trim_indent

async def generate_python_models(
    json_payload: str, root_element: str
) -> List[GeneratedFile]:
    models: List[str] = [trim_indent(
        """from typing import List
        from pydantic import BaseModel
        """)]
    modeler = Modeler()

    modeler.analyze(json_payload.encode(), root_element)
    for class_def in modeler.get_classes():
        models.append(generate_py_model(class_def))
    return [
        GeneratedFile(
            file_name="models.py",
            content = "\n\n".join(models)
        )
    ]

def generate_py_model(class_def: ClassDef) -> str:
    model = f"class {class_def.name}(BaseModel):\n"
    for field in class_def.fields:
        field_name = snake_case(field.name)
        field_type = to_py_type(field.type)
        model += f"    {field_name}: {field_type}\n"

    return model


def to_py_type(type: ValueType) -> str:
    if isinstance(type, ClassDef):
        return type.name
    elif isinstance(type, ListDef):
        return f"List[{to_py_type(type.elem_type)}]"
    elif type == 'String':
        return 'str'
    elif type == 'boolean':
        return 'bool'
    else:
        return str(type)

