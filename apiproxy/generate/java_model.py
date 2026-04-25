from ..service.models import GeneratedFile
from ..service.str_util import trim_indent
from .naming import camel_case, pascal_case
from .modeler import ListDef, ClassDef, ValueType


def generate_java_model(class_def: ClassDef) -> GeneratedFile:

    return GeneratedFile(
        file_name=f"src/main/java/com/example/generated/model/{class_def.name}.java",
        content=generate_java_class(class_def),
    )


def generate_java_class(class_def: ClassDef) -> str:
    field_decls = [
        f"private {to_java_type(field.type)} {camel_case(field.name)};"
        for field in class_def.fields
    ]

    accessors = []
    for field in class_def.fields:
        java_type = to_java_type(field.type)
        java_name = camel_case(field.name)
        getter = ("is" if field.type == "boolean" else "get") + pascal_case(field.name)
        setter = "set" + pascal_case(field.name)
        json_annotation = f'@JsonProperty("{field.name}")'

        accessors.append(f"""
            {json_annotation}
            public {java_type} {getter}() {{
                return this.{java_name};
            }}
            
            public void {setter}({java_type} {java_name}) {{
                this.{java_name} = {java_name};
            }}

            public {class_def.name} {java_name}({java_type} {java_name}) {{
                this.{java_name} = {java_name};
                return this;
            }}
        """)

    return trim_indent(f"""
        package com.example.generated.model;
        
        import com.fasterxml.jackson.annotation.JsonProperty;
                       
        public class {class_def.name} {{
            {"\n            ".join(field_decls)}
            {"\n".join(accessors)}
        }}
        """)


def to_java_type(type: ValueType) -> str:
    if isinstance(type, ClassDef):
        return type.name
    elif isinstance(type, ListDef):
        return "List<" + to_java_type(type.elem_type) + ">"
    elif type == "String":
        return "String"
    elif type == "int":
        return "int"
    elif type == "double":
        return "double"
    elif type == "None":
        return "null"
    elif type == "*":
        return "Object"
    else:
        print(f"to_java_type({type})")
        return str(type)
