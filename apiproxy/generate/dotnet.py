from typing import List

from .naming import camel_case, guess_entity_name
from .modeler import ClassDef, ListDef, Modeler, ValueType, pascal_case
from ..service.models import GeneratedFile, Traffic
from ..service.str_util import split_path, trim_indent


def get_cs_type(type: ValueType) -> str:
    if isinstance(type, ClassDef):
        return type.name
    elif isinstance(type, ListDef):
        return "List<" + get_cs_type(type.elem_type) + ">"
    elif type == "String":
        return "string"
    elif type == "int":
        return "int"
    elif type == "double":
        return "double"
    elif type == "None":
        return "Object"
    elif type == "Object":
        return "Object"
    else:
        print(f"get_cs_type({type})")
        return str(type)


def generate_cs_model(class_def: ClassDef) -> GeneratedFile:
    content = trim_indent(f"""
        namespace Example.Models;
                          
        public class {class_def.name}
        """)
    content += "{\n"
    for field in class_def.fields:
        content += f'    [JsonPropertyName("{field.name}")]\n'
        content += f"    public {get_cs_type(field.type)}? {pascal_case(field.name)} {{ get; set; }}\n\n"
    content += "}\n"

    return GeneratedFile(file_name=f"Models/{class_def.name}.cs", content=content)


async def generate_asp_net_api(traffic: Traffic) -> List[GeneratedFile]:
    op_name = guess_entity_name(traffic.method, traffic.url)
    service_name = "ExampleService"

    files: List[GeneratedFile] = []
    modeler = Modeler()

    if traffic.req_body:
        request_class = pascal_case(op_name) + "Request"
        parameters = f"{request_class} request"
        parameter_vars = "request"
        modeler.analyze(traffic.req_body, request_class)

    else:
        request_class = None
        parameters = ""
        parameter_vars = ""

    if traffic.resp_body:
        response_class = "Response"
        modeler.analyze(traffic.resp_body, response_class)

    for class_def in modeler.get_classes():
        files.append(generate_cs_model(class_def))

    method = traffic.method
    base_path, method_path = split_path(traffic.url)
    op_name = guess_entity_name(method, method_path)

    if method == "GET":
        method_annotation = f'[HttpGet("{method_path}")]'
    elif method == "POST":
        method_annotation = f'[HttpPost("{method_path}")]'
    elif method == "PUT":
        method_annotation = f'[HttpPut("{method_path}")]'
    elif method == "DELETE":
        method_annotation = f'[HttpDelete("{method_path}")]'
    elif method == "PATCH":
        method_annotation = f'[HttpPatch("{method_path}")]'
    else:
        return files

    if traffic.resp_body:
        response_class = pascal_case(op_name) + "Response"
    else:
        response_class = "String"

    controller = trim_indent(f"""
        using Microsoft.AspNetCore.Mvc;
        using Example.Models;
        
        namespace Example.Controllers;
                             
        [ApiController]
        [Route("[controller]")]
        public class ExampleController : ControllerBase
        {{
            private {service_name} {camel_case(service_name)};

            public ExampleController({service_name} {camel_case(service_name)})
            {{
                this.{camel_case(service_name)} = {camel_case(service_name)};
            }}

            {method_annotation}
            public async {response_class} {op_name}({parameters})
            {{
                var response = await {service_name}.{op_name}({parameter_vars});

                return response;
            }}
        }}
        """)

    files.append(
        GeneratedFile(file_name="Controllers/Controller.cs", content=controller)
    )

    return files
